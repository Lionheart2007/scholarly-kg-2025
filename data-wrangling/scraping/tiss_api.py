
api_base_url = "https://tiss.tuwien.ac.at/api"

api_url_organigram = api_base_url + "/orgunit/v23/organigramm"

def get_api_url_organigram():
    return api_url_organigram

api_url_orgunit_code_template = api_base_url + "/orgunit/v23/code/{orgunit_code}"

def get_api_url_orgunit_code(orgunit_code):
    return api_url_orgunit_code_template.format(orgunit_code=orgunit_code)

api_url_orgunit_id_template = api_base_url + "/orgunit/v23/id/{orgunit_id}"

def get_api_url_orgunit_id(orgunit_id):
    return api_url_orgunit_id_template.format(orgunit_id=orgunit_id)

api_url_orgunit_oid_template = api_base_url + "/orgunit/v23/oid/{orgunit_code}?persons={persons}?recursive={recursive}?intern={intern}"

def get_api_url_orgunit_oid(orgunit_code, intern=True, persons=True, recursive=True):
    return api_url_orgunit_oid_template.format(orgunit_code=orgunit_code, persons=persons, recursive=recursive, intern=intern)

api_url_orgunit_number_template = api_base_url + "/orgunit/v23/number/{orgunit_number}"

def get_api_url_orgunit_number(orgunit_number):
    return api_url_orgunit_number_template.format(orgunit_number=orgunit_number)
api_url_person_id_template = api_base_url + "/person/v23/oid/{person_id}?intern={intern}?locale=de"

def get_api_url_person_id(person_id, intern=True):
    return api_url_person_id_template.format(person_id=person_id, intern=intern)

api_url_person_oid_template = api_base_url + "/person/v23/oid/{person_oid}?intern={intern}?locale=de"

def get_api_url_person_oid(person_oid, intern=True):
    return api_url_person_oid_template.format(person_oid=person_oid, intern=intern)
