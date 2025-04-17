api_base_url = "https://tiss.tuwien.ac.at/api"

api_url_organigram = api_base_url + "/orgunit/v23/organigramm"
api_url_orgunit_id_template = api_base_url + "/orgunit/v23/oid/{orgunit_code}?persons={persons}?recursive={recursive}?intern={intern}"
api_url_person_id_template = api_base_url + "/person/v23/id/{person_id}?intern={intern}"

def get_api_url_orgunit_id(orgunit_code, persons=True, recursive=True, intern=True):
    return api_url_orgunit_id_template.format(orgunit_code=orgunit_code, persons=persons, recursive=recursive, intern=intern)

def get_api_url_person_id(person_id, intern=True):
    return api_url_person_id_template.format(person_id=person_id, intern=intern)
