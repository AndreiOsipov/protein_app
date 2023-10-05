import pytest
import json
from .proteins_scripts.elm_ids_script import get_elm_ids_by_squence_id

def test_for_RB1_human():
    with open('tests/really_ids.json') as f:
        rb1_human_ids_list = json.load(f)['RB1_human']
        rb1_human_from_program = get_elm_ids_by_squence_id('RB1_human')

        assert len(rb1_human_ids_list) == len(rb1_human_from_program)
        assert rb1_human_ids_list == rb1_human_from_program