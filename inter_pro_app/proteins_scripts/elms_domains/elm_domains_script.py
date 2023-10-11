DOMAINS_URL = 'http://elm.eu.org/interactiondomains.tsv'
DOMAIN_FILE_NAME = 'elm_interaction_domains.tsv'
import os
import requests
import csv
import logging
import os
from inter_pro_app.loggers.loggers import  LoggerGetter
#разобраться как именно работает запись в файл
#добавить логи
#добавить try/except
class DomainsGetter:

    '''
    - класс для получения списка доменов взаимодействия
    '''
    def _download_to_domains_file(self, path_to_domain_file):
        loggerg_etter = LoggerGetter()
        logger = loggerg_etter.get_logger('elm_domains', logging.INFO)
        res = requests.get(DOMAINS_URL)
        content = str.join('',res.text.split('\n'))
        with open(path_to_domain_file, 'a') as file:
            file.write(content)
        logger.info(msg=f'redownloadad domain was succes')

    def _read_domains_file(self, path_to_domain_file):
        domains:dict[str, set[str]] = {}
        loggerg_etter = LoggerGetter()
        logger = loggerg_etter.get_logger('elm_domains', logging.INFO)

        with open(path_to_domain_file,encoding='utf-8', mode='r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if row[0] not in domains.keys():
                    domains[row[0]] = set([row[1]])
                else:
                    domains[row[0]].add(row[1])
        logger.info(msg=f'{len(domains.keys())} domains was downloaded and readed')
        
        return domains

    def get_all_domains(self, file_name='elm_interaction_domains.tsv'):
        '''
        - выдает словарь всевозможных доменов взаимодействия
        - ключ -- id протеина
        - значение -- список доменов, по которым он взаимодействует 
        '''
        this_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(this_dir)
        cached_resources_dir = os.path.join(parent_dir, 'cached_resources')
        path_to_domain_file = os.path.join(cached_resources_dir, file_name)
        self._download_to_domains_file(path_to_domain_file)
        return self._read_domains_file(path_to_domain_file)