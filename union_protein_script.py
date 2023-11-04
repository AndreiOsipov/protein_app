import csv
import os
import time
import logging

from dataclasses import dataclass
from inter_pro_app.proteins_scripts.domains_info.uniprot_genes_script import GenesGetter
from inter_pro_app.proteins_scripts.domains_info.InterPro_script import Protein, InterProConnect

from inter_pro_app.proteins_scripts.elms_domains.elm_domains_script import DomainsGetter
from inter_pro_app.proteins_scripts.elms_domains.elm_ids_script import get_elm_ids_by_squence_id
from inter_pro_app.loggers.loggers import LoggerGetter
# --------------------------- логика ---------------------------
# - вынести в метод обработку папок
# - проверить надежность получения списка elm через тесты
# - проверить надежность создания структуры папок (загрузки elm_id) на sequence_id через тесты
# -> т.е. механизм, определяющий домайны для загрузки на конкретный rlm работает верно
# - проверить надежность загрузки самих домайнов-протеинов (PFXXXXX)
# -> что загружаются все со страницы(proteins_count верный)
# -> что звгрузка одного и того же домайна из разных elm одинакова
# -> что единственный вариаент, при котором загрзука не прошла -- реальное отсутсутствие протеина в базе(при этом на него явно есть ссылка в elm-таблице)  
# --------------------------- Django ---------------------------
# - 
@dataclass
class ProteinInfo:
    protein: Protein
    genes:list[str]

class GenesGetterUnionInterProConnect:
    def __init__(self, domain_name: str, test) -> None:
        self.domain_name = domain_name
        self.test = test
        self.downloaded_proteins_count = 0
        
        try:
            self.connect = InterProConnect(domain_name, self.test)
            self.proteins_count = self.connect.proteins_count
        except:
            self.connect = None
            self.proteins_count = 0

    @property
    def proteins_downloaded_persent(self):
        if self.proteins_count > 0:
            return round((self.downloaded_proteins_count / self.proteins_count * 100), 2)
        return 0.0
    
    def get_protein_and_gene(self):
        genes_getter = GenesGetter()
        if self.connect:
            for proteins_lst in self.connect.output_list():
                if proteins_lst:
                    for protein in proteins_lst:
                        genes = genes_getter.get_genes_list_by_acces_id(protein.accession)
                        self.downloaded_proteins_count += 1
                        yield ProteinInfo(protein, genes)
                else:
                    yield
        else:
            yield
        
class DownloaderDomainConnect:
    def __init__(self, domain_name:str, test_download:bool) -> None:
        self.api = GenesGetterUnionInterProConnect(domain_name, test_download)

    def dowmload_domain_info_to_file(self, file_name: str):
        '''
        отправляет запрос на закачку и записывает скаченную информацию о домайне в таблицу
        '''
        #TODO прописыать запись таблицы с уникальными генами
        #TODO определить локальный timeout
        full_file_name = file_name
        logger = LoggerGetter().get_logger('union_api', logging.INFO)

        with open(full_file_name, 'wt') as file:
            writer = csv.writer(file, delimiter='\t', lineterminator='\n')
            writer.writerow(['accession id','name','scientific name','source database', 'taxId', 'length','entry protein locations', 'gene names'])    
            for protein_info in self.api.get_protein_and_gene():
                if protein_info is None:
                    return
                writer.writerow([
                    protein_info.protein.accession,
                    protein_info.protein.name,
                    protein_info.protein.scientificName,
                    protein_info.protein.source_database,
                    protein_info.protein.taxId,
                    protein_info.protein.length,
                    protein_info.protein.entry_protein_locations,
                    ','.join(protein_info.genes)])
        
        logger.info(msg=f'{self.api.domain_name} domain: {self.api.downloaded_proteins_count} from {self.api.proteins_count} proteins was downloaded and write to {full_file_name} file')

class ProteinsSquenceDownloader:

    def __init__(self) -> None:
        self.path_to_downloaders = os.path.join(os.path.dirname(os.path.abspath(__file__)),'downloaded_sequnce_id_proteins')
        self.test = False
        self.domain_getter = DomainsGetter()
        self.domains = self.domain_getter.get_all_domains()

        self.logger_getter = LoggerGetter()
        self.logger = self.logger_getter.get_logger('union_api', logging.INFO)
        self.count_of_downloaded_elm = 0
    
    def _build_dir_if_not_exist(self, dir_path):
        if os.path.exists(dir_path):
            return
        os.mkdir(dir_path)

    def _download_table(self, domain_name: str, elm_dir: str, test: bool):
        full_path_to_domain_table = os.path.join(elm_dir, f'{domain_name}.tsv')
        downloader = DownloaderDomainConnect(domain_name, test)
        downloader.dowmload_domain_info_to_file(full_path_to_domain_table)
    
    def _download_tables(self, domains:dict[str, set[str]], elm_name: str, elm_dir: str):
        downloaded_domains = os.listdir(elm_dir)
        last_domain = ''
        last_domain_was_downloaded = False


        if elm_name in domains.keys():
            for idx, domain_name in enumerate(domains[elm_name]):
                if domain_name in downloaded_domains and idx != len(domains) - 1:
                    last_domain = domain_name
                else:
                    if not (last_domain_was_downloaded) and idx != len(domains) - 1 and last_domain != '':
                        #перезагрузка предыдущей таблицы
                        self._download_table(last_domain, elm_dir, self.test)
                        last_domain_was_downloaded = True
                    self._download_table(domain_name, elm_dir, self.test)
    
    def _download_elm(self, sequence_dir:str, elm_id:str, idx: int, elm_ids_len: int):
        elm_dir = os.path.join(sequence_dir, elm_id)
        self._build_dir_if_not_exist(elm_dir)
        self._download_tables(self.domains, elm_id, elm_dir)
        self.count_of_downloaded_elm+=1
        self.logger.info(msg=f'{elm_id} proteins was downloaded it is {idx+1} in {elm_ids_len} elms')

    def download_proteins_sequence_data(self, sequence_id):
        sequence_dir = os.path.join(self.path_to_downloaders, sequence_id)
        self._build_dir_if_not_exist(sequence_dir)
        elm_ids = get_elm_ids_by_squence_id(sequence_id)
        elm_ids_len = len(elm_ids)
        last_downloaded_elm = ''
        last_elm_folder_was_filled = False

        for idx, elm_id in enumerate(elm_ids):
            downloaded_elm_ids = os.listdir(sequence_dir)
            if elm_id in downloaded_elm_ids and idx != elm_ids_len - 1:
                last_downloaded_elm = elm_id
            else:
                if self.count_of_downloaded_elm > 0 and self.count_of_downloaded_elm % 10 == 0:
                    time.sleep(61)
                
                if not(last_elm_folder_was_filled) and idx != elm_ids_len - 1 and last_downloaded_elm != '':
                    #дозагрузка предыдущего elm
                    self._download_elm(sequence_dir, last_downloaded_elm, idx, elm_ids_len)
                    last_elm_folder_was_filled = True
                self._download_elm(sequence_dir, elm_id, idx, elm_ids_len)

if __name__ == '__main__':
    loader = ProteinsSquenceDownloader()
    loader.download_proteins_sequence_data('KMT5C_HUMAN')

# DEG_SCF_TRCP1_1 + следующий  -- проверить на адекватность + проверить предыдущие

