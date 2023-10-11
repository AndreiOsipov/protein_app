import pytest
import json
from ..proteins_scripts.elms_domains.elm_ids_script import get_elm_ids_by_squence_id, FinishUrlGetter, ProteinsElmNameGetter
BASE_URL_BEGIN = 'http://elm.eu.org/cgimodel.py?fun=Submit&swissprotId='

# def test_for_RB1_human():
#     with open('really_ids.json') as f:
#         rb1_human_ids_list = json.load(f)['RB1_human']
#         rb1_human_from_program = get_elm_ids_by_squence_id('RB1_human')

#         assert len(rb1_human_ids_list) == len(rb1_human_from_program)
#         assert rb1_human_ids_list == rb1_human_from_program

def test_for_RB1_human_url():
    sequence_id = 'RB1_human'
    right_url = 'http://elm.eu.org/cgimodel.py?fun=smartResult&userId=QiKPcvQDai&EXPECT_CUTOFF=100&r=1&bg=on'
    
    url_from_func = FinishUrlGetter().get_finish_url_from_medium_url(f'{BASE_URL_BEGIN}{sequence_id}')
    print('right url',right_url)
    print('url from func',url_from_func)
    assert right_url == url_from_func