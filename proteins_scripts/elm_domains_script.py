DOMAINS_URL = 'http://elm.eu.org/interactiondomains.tsv'
DOMAIN_FILE_NAME = 'elm_interaction_domains.tsv'
import os
import requests
import csv
#разобраться как именно работает запись в файл
#добавить логи
#добавить try/except

def _download_to_domains_file(path_to_domain_file):
    res = requests.get(DOMAINS_URL)
    content = str.join('',res.text.split('\n'))
    with open(path_to_domain_file, 'a') as file:
        file.write(content)

def _read_domains_file(path_to_domain_file):
    domains:dict[str, set[str]] = {}
    with open(path_to_domain_file,encoding='utf-8', mode='r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            if row[0] not in domains.keys():
                domains[row[0]] = set([row[1]])
            else:
                domains[row[0]].add(row[1])
    print(f'домайны будут {len(domains)}')
    return domains

def get_all_domains(file_name='elm_interaction_domains.tsv'):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(this_dir)
    cached_resources_dir = os.path.join(parent_dir, 'cached_resources')
    path_to_domain_file = os.path.join(cached_resources_dir, file_name)
    if not(os.path.exists(path_to_domain_file)):   
        _download_to_domains_file(path_to_domain_file)
    
    return _read_domains_file(path_to_domain_file)