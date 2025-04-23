import requests
from tiss_api import *
from dotenv import load_dotenv
import os
from neo4j_database_operations import *
import re
import time
import json

load_dotenv()

NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")

LABEL_PERSON = "Person"
LABEL_ORG = "Organisation"
LABEL_FUNCTION = "Function"

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

def process_employee(employee, org_oid, org_code):  
        """
        Processes each employee by fetching their data and adding them to the database.
        """
        person_id = employee['oid']
        fetched_person_data = fetch_data_from_api(get_api_url_person_id(person_id)) 

        print(f"{employee['first_name']} {employee['last_name']}")
        
        person_properties = {
            "id": employee['oid'],
            "first_name": employee['first_name'],
            "last_name": employee['last_name'],
            "preceding_titles": employee['preceding_titles'],
            "postpositioned_titles": employee['postpositioned_titles'],
            "picture_link": employee['picture_uri'],
            "phone_number": employee.get('phone_numbers', [None])[0],
            "email": employee['main_email'],
        }

        # Initial add none existing person
        if not db.node_exists(person_id):
            db.add_node(LABEL_PERSON, person_properties)
        
        # Add function relationships to the person
        if True:
            #for role in fetched_person_data['employee']:
                
                function_tiss_id = employee.get('function_tiss_id', None)
                display_function = employee.get('display_function', None)
    
                function_group_tiss_id = employee.get('function_group_tiss_id', None)
                display_function_group = employee.get('display_function_group', None)
    
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
                    'name': employee['display_function_group']
                }
                #if role.get('websites'):
                #    relationship_properties["website"] = json.dumps(role['websites'])

                db.add_relationship_if_not_exists(
                    function_id, 
                    person_id, 
                    "ROLE", 
                    relationship_properties
                )

def add_people_to_org_einheit(org_oid, org_code):

    api_url = get_api_url_orgunit_id(org_oid, persons=True, recursive=True, intern=True)
    orgunit_data = fetch_data_from_api(api_url, {"oid": org_oid})
    employees = orgunit_data.get('employees', [])
    
    for employee in employees:
        process_employee(employee, org_oid, org_code)

def add_org_nodes(faculty_data):
            node_data = {
                "id": faculty_data['oid'],
                "id_number": faculty_data['code'],
                "name": faculty_data['name_en'],
                "phone_numbers": faculty_data.get('phone_numbers', []),
                "website": json.dumps(faculty_data.get('websites', [])) if faculty_data.get('websites') else None,
                "emails": faculty_data['emails'][0] if len(faculty_data.get('emails', [])) == 1 else (json.dumps(faculty_data.get('emails', [])) if faculty_data.get('emails') else None),
                "address": "; ".join([
                    f"{remove_umlauts(address.get('street', ''))}, {address.get('zip_code', '')} {remove_umlauts(address.get('city', ''))}, {remove_umlauts(address.get('country', ''))}, c/o {address.get('co', '')}".strip(", ")
                    for address in faculty_data.get('addresses', [])
                ]) if faculty_data.get('addresses') else None
            }
            # Remove keys with None values
            node_data = {k: v for k, v in node_data.items() if v is not None}
            db.add_node(LABEL_ORG, node_data)

def add_faculties_to_graph(raw_data):
    orgs = raw_data.get('children', [])[6:]
    for faculty in orgs:
        fac_code = clean_symbols(faculty.get('code', ''))
        fac_id = faculty.get('oid', '')
        faculty_data = fetch_data_from_api(get_api_url_orgunit_id(faculty.get('oid', '')))
        print(f"{faculty_data.get('name_en', '')}")
        if not faculty_data:
            continue
        add_org_nodes(faculty_data)
        add_people_to_org_einheit(fac_id, fac_code)

        if "child_orgs_refs" in faculty_data:
            for institution in faculty_data.get('child_orgs_refs', []):   
                inst_code = clean_symbols(institution.get('code', ''))
                inst_id = institution.get('oid', '')
                institution_data = fetch_data_from_api(get_api_url_orgunit_id(inst_id))
                print(f"  {institution.get('name_en', '')}")
                if institution_data:  
                    add_org_nodes(institution_data)
                    db.add_relationship(fac_id, inst_id, "HAS_INSTITUTION")
                    add_people_to_org_einheit(inst_id, inst_code)

                if "child_orgs_refs" in institution_data:
                    for department in institution_data.get('child_orgs_refs', []):
                        dep_code = clean_symbols(department.get('code', ''))
                        dep_id = department.get('oid', '')
                        department_data = fetch_data_from_api(get_api_url_orgunit_id(dep_id))
                        print(f"    {department.get('name_en', '')}")
                        if department_data:
                            add_org_nodes(department_data)
                            db.add_relationship(inst_id, dep_id, "HAS_DEPARTMENT")
                            add_people_to_org_einheit(dep_id, dep_code)

                        if "child_orgs_refs" in department_data:
                            for research_group in department_data.get('child_orgs_refs', []):
                                rg_code = clean_symbols(research_group.get('code', ''))
                                rg_id = research_group.get('oid', '')
                                research_group_data = fetch_data_from_api(get_api_url_orgunit_id(rg_id))
                                print(f"      {research_group.get('name_en', '')}")
                                if research_group_data:
                                    add_org_nodes(research_group_data)
                                    db.add_relationship(dep_id, rg_id, "HAS_RESEARCH_GROUP")
                                    add_people_to_org_einheit(rg_id, rg_code)


raw_data = fetch_data_from_api(api_url_organigram.format())
start_time = time.time()

db.clear_database()
print("Database cleared.")

print("Adding faculties to graph...")

add_faculties_to_graph(raw_data)

end = time.time()

print("Time taken in hh:mm:ss:", time.strftime("%H:%M:%S", time.gmtime(end - start_time)))
