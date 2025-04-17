import requests
from tiss_api import *
from neo4j_database_operations import *

def fetch_data_from_api(api_url):
    """Fetches data from the given REST API URL."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {api_url}: {e}")
        return None

raw_data = fetch_data_from_api(api_url_organigram.format())
seniorGovBodies = raw_data['children']

faculties = [x for x in seniorGovBodies if x['name_de'].startswith('Fak')]
print(len(faculties))

clear_database()


def add_people_to_org_einheit(org_oid, org_label, org_type):
    api_url = get_api_url_orgunit_id(org_oid, persons=True, recursive=True, intern=True)
    orgunit_data = fetch_data_from_api(api_url)
    if orgunit_data:
        for person in orgunit_data['employees']:
            person_id = person['oid']
            add_node(f"Person_{person_id}", {
                "first_name": person['first_name'],
                "last_name": person['last_name'],
                "id": person_id,
                "tiss_id": person.get('tiss_id'),
                "oid": person.get('oid'),
                "old_tiss_ids": person.get('old_tiss_ids', []),
                "pseudoperson": person.get('pseudoperson'),
                "preceding_titles": person.get('preceding_titles'),
                "postpositioned_titles": person.get('postpositioned_titles'),
                "orcid": person.get('orcid'),
                "card_uri": person.get('card_uri'),
                "picture_uri": person.get('picture_uri'),
                "main_phone_number": person.get('main_phone_number'),
                "main_email": person.get('main_email'),
                "other_emails": person.get('other_emails', []),
                "additional_infos": person.get('additional_infos', []),
                "function_tiss_id": person.get('function_tiss_id'),
                "display_function": person.get('display_function'),
                "function_group_tiss_id": person.get('function_group_tiss_id'),
                "display_function_group": person.get('display_function_group')
            })
            add_relationship(f"{org_type}{org_oid}", f"Person_{person_id}", "HAS_PERSON")


def add_faculties_to_graph(faculties):
    for faculty in faculties:
        add_node(f"Faculty_{faculty['oid']}", 
                 {"name": faculty['name_en'], "id": faculty['oid']})
        if "children" in faculty:
            for institution in faculty['children']:
                add_node(f"Institution_{institution['oid']}", {"name": institution['name_en'], "id": institution['oid']})
                add_relationship(f"Faculty_{faculty['oid']}", f"Institution_{institution['oid']}", "HAS_INSTITUTION")
                add_people_to_org_einheit(institution['oid'], institution['name_en'], "Institution_")
                if "children" in institution:
                    for department in institution['children']:
                        add_node(f"Department_{department['oid']}", {"name": department['name_en'], "id": department['oid']})
                        add_relationship(f"Institution_{institution['oid']}", f"Department_{department['oid']}", "HAS_DEPARTMENT")
                        add_people_to_org_einheit(department['oid'], department['name_en'], "Department_")
                        if "children" in department:
                            for research_group in department['children']:
                                add_node(f"ResearchGroup_{research_group['oid']}", {"name": research_group['name_en'], "id": research_group['oid']})
                                add_relationship(f"Department_{department['oid']}", f"ResearchGroup_{research_group['oid']}", "HAS_RESEARCH_GROUP")
                                add_people_to_org_einheit(research_group['oid'], research_group['name_en'], "ResearchGroup_")

add_faculties_to_graph(faculties)
