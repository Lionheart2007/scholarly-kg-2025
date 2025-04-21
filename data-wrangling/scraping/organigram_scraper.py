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

label_person = "Person"
label_organisation = "Organisation"
label_function = "Function"

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

def process_employee(employee, org_label, org_oid):    
        """
        Processes each employee by fetching their data and adding them to the database.
        """
        person_id = employee['oid']
        fetched_person_data = fetch_data_from_api(get_api_url_person_id(person_id))  
        print(f"            {employee['first_name']} {employee['last_name']}")
        
        person_data = {
            "id": employee['oid'],
            "first_name": employee['first_name'],
            "last_name": employee['last_name'],
            "preceding_titles": employee['preceding_titles'],
            "postpositioned_titles": employee['postpositioned_titles'],
            "picture_link": employee['picture_uri'],
            "phone_number": employee.get('phone_numbers', [None])[0],
            "email": employee['main_email'],
        }

        if not db.node_exists(person_id):
            db.add_node(label_person, person_data)
        
        if fetched_person_data:
            for role in fetched_person_data['employee']:
                function_group_relation = "DELEGATION"
                id = (f"{role['function_tiss_id']}_{org_oid}")
                function_properties = {
                    "id": id,
                    "abbreviation": role['function_tiss_id'],
                    "org_id": org_oid,
                    "name": role['display_function_group']
                }

                if not db.node_exists(id):
                    db.add_node(label_function, function_properties)
                    db.add_relationship(org_oid, id, function_group_relation)
                
                db.add_relationship_if_not_exists(
                    person_id, 
                    id, 
                    "ROLE", 
                    {'name': role['display_function_group']}
                )
        
def add_people_to_org_einheit(org_oid, org_label):

    api_url = get_api_url_orgunit_id(org_oid, persons=True, recursive=True, intern=True)
    orgunit_data = fetch_data_from_api(api_url, {"oid": org_oid})
    employees = orgunit_data.get('employees', [])
    for employee in employees:
        process_employee(employee, org_label, org_oid)

def add_org_nodes(faculty_data, fac_label):
            db.add_node(label_organisation,
            {"id": faculty_data['oid'],
             "name": faculty_data['name_en'],
             "phone_numbers": faculty_data.get('phone_numbers', []),
             "website": json.dumps(faculty_data.get('websites', [])),
             "emails": faculty_data['emails'][0] if len(faculty_data.get('emails', [])) == 1 else json.dumps(faculty_data.get('emails', [])),
             "address": json.dumps([
                 {
                 "street": remove_umlauts(address.get("street")),
                 "zip_code": address.get("zip_code"),
                 "city": remove_umlauts(address.get("city")),
                 "country": remove_umlauts(address.get("country")),
                 "co": address.get("co")
                 } for address in faculty_data.get('addresses', [])
             ])
        })

def add_faculties_to_graph(raw_data):
    orgs = raw_data['children']
    for faculty in orgs:
        fac_label = clean_symbols(faculty['code'])
        fac_id = faculty['oid']

        faculty_data = fetch_data_from_api(get_api_url_orgunit_id(faculty['oid']))
        if not faculty_data:
            continue
        add_org_nodes(faculty_data, fac_label)
        print(f"{faculty_data['name_en']}")

        if "child_orgs_refs" in faculty_data:
            for institution in faculty_data['child_orgs_refs']:
                inst_label = clean_symbols(institution['code'])
                inst_id = institution['oid']
                institution_data = fetch_data_from_api(get_api_url_orgunit_id(institution['oid']))
                if not institution_data:
                    continue
                add_org_nodes(institution_data, inst_label)
                db.add_relationship(fac_id, inst_id, "HAS_INSTITUTION")
                print(f"  {institution['name_en']}")
                add_people_to_org_einheit(institution['oid'], inst_label)
                if "child_orgs_refs" in institution_data:
                    for department in institution_data['child_orgs_refs']:
                        dep_label = clean_symbols(department['code'])
                        dep_id = department['oid']
                        department_data = fetch_data_from_api(get_api_url_orgunit_id(department['oid']))
                        if not department_data:
                            continue
                        add_org_nodes(department_data, dep_label)
                        db.add_relationship(inst_id, dep_id, "HAS_DEPARTMENT")
                        print(f"    {department['name_en']}")
                        add_people_to_org_einheit(department['oid'], dep_label)
                        if "child_orgs_refs" in department_data:
                            for research_group in department_data['child_orgs_refs']:
                                rg_label = clean_symbols(research_group['code'])
                                rg_id = research_group['oid']
                                research_group_data = fetch_data_from_api(get_api_url_orgunit_id(research_group['oid']))
                                if not research_group_data:
                                    continue
                                add_org_nodes(research_group_data, rg_label)
                                db.add_relationship(dep_id, rg_id, "HAS_RESEARCH_GROUP")
                                print(f"      {research_group['name_en']}")
                                add_people_to_org_einheit(research_group['oid'], rg_label)


raw_data = fetch_data_from_api(api_url_organigram.format())
start_time = time.time()

db.clear_database()
print("Database cleared.")
add_faculties_to_graph(raw_data)

end = time.time()

print("Time taken in hh:mm:ss:", time.strftime("%H:%M:%S", time.gmtime(end - start_time)))
