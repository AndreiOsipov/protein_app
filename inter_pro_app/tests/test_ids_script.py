import pytest
import json
from ..proteins_scripts.elms_domains.elm_ids_script import get_elm_ids_by_squence_id
BASE_URL_BEGIN = 'http://elm.eu.org/cgimodel.py?fun=Submit&swissprotId='

def test_for_correct_find_elm_list():
    with open('really_ids.json') as f:
        elms_dict = json.load(f)['test_elms']
        for elm in elms_dict.keys():
            elm_lst = elms_dict[elm]
            rb1_human_from_program = get_elm_ids_by_squence_id(elm)

            assert len(elm_lst) == len(rb1_human_from_program)
            assert elm_lst == rb1_human_from_program