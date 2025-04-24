import requests
from tiss_api import *
from dotenv import load_dotenv
import os
from neo4j_database_operations import *
import re
import time
import json
import uuid

load_dotenv()

NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")

LABEL_PERSON = "Person"
LABEL_ORG = "Organisation"
LABEL_FUNCTION = "Function"

TYPE_OOG = "OOG" # Senior Governance

TYPE_REK = "REK" # Rector
TYPE_VIR = "VIR" # Vice-Rector

TYPE_ABT = "ABT" # Department
TYPE_FAB = "FAB" # Service Unit

TYPE_FAK = "FAK" # Faculty
TYPE_INS = "INS" # Institution
TYPE_FOB = "FOB" # Department
TYPE_FOG = "FOG" # Research Group
TYPE_DEK = "DEK" # Deanery

TYPE_GRU = "GRU"
TYPE_SFO = "SFO" 
TYPE_SON = "SON"

db = Neo4jDatabase(NEO4J_URI, (NEO4J_USERNAME, NEO4J_PASSWORD))

def fetch_data_from_api(api_url, params=None):
    """Fetches data from the given REST API URL."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {api_url}: {e}, for params: {params}")
        return None
    
def clean_symbols(label):
    """Cleans the label by replacing spaces with underscores and removing unwanted characters."""
    label = re.sub(r"[^\w\s]", "", label)  # Remove all non-alphanumeric characters except spaces
    label = label.replace(" ", "_")  
    return label

def remove_umlauts(text):
    translation_map = {
        ord('ä'): 'ae',
        ord('ö'): 'oe',
        ord('ü'): 'ue',
        ord('ß'): 'ss',
        ord('Ä'): 'Ae',
        ord('Ö'): 'Oe',
        ord('Ü'): 'Ue'
    }
    trans_table = str.maketrans(translation_map)
    label = text.translate(trans_table)
    return label

def process_person(person, org_oid, org_code):  
    """
    Processes each employee by fetching their data and adding them to the database.
    """
    person_id = person['oid']

    if not person_id:
        tiss_id = person.get('tiss_id', None)
        if not tiss_id:
            print(f"Entity cannot be processed, no tiss_id found for {person}")
            return
        fetched_person_data = fetch_data_from_api(get_api_url_person_id(tiss_id, intern=True))
        if not fetched_person_data:
            print(f"Entity cannot be processed, no data found for {person}")
            return
        fetched_person_data['oid'] = str(uuid.uuid4())
        person_id = fetched_person_data.get('oid')
    else:
        fetched_person_data = fetch_data_from_api(get_api_url_person_oid(person_id, intern=True)) 

    person_properties = {
        "id": fetched_person_data.get('oid'),
        "first_name": fetched_person_data.get('first_name'),
        "last_name": fetched_person_data.get('last_name'),
        "preceding_titles": fetched_person_data.get('preceding_titles'),
        "postpositioned_titles": fetched_person_data.get('postpositioned_titles'),
        "picture_link": fetched_person_data.get('picture_uri'),
        "phone_number": fetched_person_data.get('main_phone_number'),
        "email": fetched_person_data.get('main_email'),
    }

    # Initial add none existing person
    if not db.node_exists(person_id):
        db.add_node(LABEL_PERSON, person_properties)
                    
    function_tiss_id = person.get('function_tiss_id', None)
    display_function = person.get('display_function', None)

    function_group_tiss_id = person.get('function_group_tiss_id', None)
    display_function_group = person.get('display_function_group', None)

    # composite key for the function
    function_id = (f"{org_code}_{display_function}".replace(" ", "_") if display_function else None)

    # Add function node if it doesn't exist
    if not db.node_exists(function_id):
        general_function_properties = {
            "id": function_id,
            "abbreviation": function_group_tiss_id,
            "name": display_function_group,
        }

        general_relation_properties = {
            "display_function": display_function,
            "function_tiss_id": function_tiss_id,
        }

        db.add_node(LABEL_FUNCTION, general_function_properties)
        db.add_relationship(
             org_oid, 
             function_id, 
             "DELEGATION", 
             general_relation_properties)
                
    # Add function relationship to the person
    #    unique function relation id
    function_relation_id = f"{org_code}_{display_function}"
    relationship_properties = {
        'id': function_relation_id,
        'name': person['display_function_group']
    }
    if person.get('websites'):
        relationship_properties["website"] = json.dumps(person['websites'])
    if person.get('other_emails'):
        relationship_properties["other_emails"] = json.dumps(person['other_emails'])

    db.add_relationship_if_not_exists(
        function_id, 
        person_id, 
        "ROLE", 
        relationship_properties
    )

def add_people_to_org(org_oid, org_code):

    api_url = get_api_url_orgunit_oid(org_oid, persons=True, recursive=True, intern=True)
    orgunit_data = fetch_data_from_api(api_url)
    employees = orgunit_data.get('employees', [])

    manager = orgunit_data.get('manager', None)
    if manager:
        manager['display_function_group'] = 'Manager'
        manager['display_function'] = 'Manager'
        employees.append(manager)
    
    for employee in employees:
        process_person(employee, org_oid, org_code)

def add_org_nodes(faculty_data):
    node_data = {
        "id": faculty_data['oid'],
        "id_number": faculty_data['code'],
        "name": faculty_data['name_en'],
    }

    if faculty_data.get('phone_numbers'):
        node_data["phone_numbers"] = [phone for phone in faculty_data['phone_numbers'] if phone]

    if faculty_data.get('websites'):
        node_data["websites"] = [website.get('uri') for website in faculty_data['websites'] if website.get('uri')]

    if faculty_data.get('emails'):
        node_data["emails"] = [email for email in faculty_data['emails'] if email]

    if faculty_data.get('addresses'):
        node_data["address"] = "; ".join(
            [
                f"{remove_umlauts(address.get('street', '')) if address.get('street') else ''} "
                f"{address.get('zip_code', '') if address.get('zip_code') else ''} "
                f"{remove_umlauts(address.get('city', '')) if address.get('city') else ''} "
                f"{remove_umlauts(address.get('country', '')) if address.get('country') else ''}"
                f"{' c/o ' + address.get('co') if address.get('co') else ''}".strip()
                for address in faculty_data['addresses']
            ]
        )


    # Remove keys with None values
    node_data = {k: v for k, v in node_data.items() if v is not None}
    db.add_node(LABEL_ORG, node_data)

def add_orgs_to_graph(raw_data):
    orgs = raw_data.get('children', [])
    # Reverse order because of constraint SUPPORT_BRANCH
    orgs = orgs[::-1]
    
    for org in orgs:
        org_code = clean_symbols(org.get('code', ''))
        org_id = org.get('oid', '')
        org_data = fetch_data_from_api(get_api_url_orgunit_oid(org_id))

        print(f"    ADDED: {org_data.get('name_en', '')}")
        
        if not org_data:
            continue
        add_org_nodes(org_data)
        add_people_to_org(org_id, org_code)

        if "child_orgs_refs" in org_data:
            for institution in org_data.get('child_orgs_refs', []):   
                inst_code = clean_symbols(institution.get('code', ''))
                inst_oid = institution.get('oid', '')
                institution_data = fetch_data_from_api(get_api_url_orgunit_oid(inst_oid))
                if institution_data:  
                    inst_type = institution_data.get('type', '')

                    relation_label = \
                        "RESEARCH" if inst_type == TYPE_INS else \
                        "SUPPORT_BRANCH" if inst_type == TYPE_OOG else \
                        "SUPPORT"

                    add_org_nodes(institution_data)
                    db.add_relationship(org_id, inst_oid, relation_label)
                    add_people_to_org(inst_oid, inst_code)

                if "child_orgs_refs" in institution_data:
                    for department in institution_data.get('child_orgs_refs', []):
                        dep_type = department.get('type', '')
                        dep_code = clean_symbols(department.get('code', ''))
                        dep_oid = department.get('oid', '')
                        department_data = fetch_data_from_api(get_api_url_orgunit_oid(dep_oid))
                        if department_data:
                            add_org_nodes(department_data)
                            if dep_type == TYPE_DEK:
                                db.add_relationship(org_id, dep_oid, "DEANERY")

                            elif dep_type == TYPE_FOB:
                                db.add_relationship(inst_oid, dep_oid, "BRANCH")
                            elif dep_type == TYPE_OOG:
                                db.add_relationship(inst_oid, dep_oid, "SUPPORT_BRANCH")
                            else:
                                db.add_relationship(inst_oid, dep_oid, "SUPPORT")

                            add_people_to_org(dep_oid, dep_code)

                        if department_data and "child_orgs_refs" in department_data:
                            for research_group in department_data.get('child_orgs_refs', []):
                                rg_code = clean_symbols(research_group.get('code', ''))
                                rg_type = research_group.get('type', '')
                                rg_oid = research_group.get('oid', '')
                                research_group_data = fetch_data_from_api(get_api_url_orgunit_oid(rg_oid))

                                if research_group_data:
                                    add_org_nodes(research_group_data)
                                    db.add_relationship(dep_oid, rg_oid, "COMPONENT")
                                        
                                    add_people_to_org(rg_oid, rg_code)

if db.is_database_running():
    db.clear_database()
    print("Neo4j database is running and has been cleared.")
else:
    print("Something went wrong with the Neo4j database connection.")
    exit()
    
raw_data = fetch_data_from_api(get_api_url_organigram().format())

start_time = time.time()

add_orgs_to_graph(raw_data)

end = time.time()

print("Time taken in hh:mm:ss:", time.strftime("%H:%M:%S", time.gmtime(end - start_time)))
