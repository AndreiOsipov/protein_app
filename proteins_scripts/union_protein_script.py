import csv
import os
from dataclasses import dataclass

from .uniprot_genes_script import GenesGetter
from .elm_ids_script import get_elm_table
from .elm_domains_script import get_all_domains
from .InterPro_script import Protein, InterProConnect


@dataclass
class ProteinInfo:
    protein: Protein
    genes:list[str]

class UnionAPI:
    def __init__(self, domain_name: str) -> None:
        self.downloaded_proteins_count = 0
        self.domain_name = domain_name
        self.connect = InterProConnect(domain_name)
        self.proteins_count = self.connect.proteins_count
        self.is_starting = False

    @property
    def proteins_downloaded_persent(self):
        return round((self.downloaded_proteins_count / self.proteins_count * 100), 2)

    def get_protein_and_gene(self):
        genes_getter = GenesGetter()
        for proteins_lst in self.connect.output_list():
            for protein in proteins_lst:
                genes = genes_getter.get_genes_list_by_acces_id(protein.accession)
                yield ProteinInfo(protein, genes)

    def write_to_file(self, file_name: str):
        self.is_starting = True
        full_file_name = file_name
        try:
            with open(full_file_name, 'at') as file:
                writer = csv.writer(file, delimiter='\t', lineterminator='\n')
                writer.writerow(['accession id','name','scientific name','source database', 'taxId', 'length','entry protein locations', 'gene names'])    
                for protein_info in self.get_protein_and_gene():
                    writer.writerow([
                        protein_info.protein.accession,
                        protein_info.protein.name,
                        protein_info.protein.scientificName,
                        protein_info.protein.source_database,
                        protein_info.protein.taxId,
                        protein_info.protein.length,
                        protein_info.protein.entry_protein_locations,
                        ','.join(protein_info.genes)])
                    self.downloaded_proteins_count += 1
            self.is_starting = False
        except:
           ...

class ProteinsSquenceDownloader:
    def __init__(self, folder_path: str) -> None:
        self.folder_path = folder_path
        self.status = ''
    
    def _build_dir_if_not_exist(self, dir_path):
        if os.path.exists(dir_path):
            print('есть такая дирректория')
            return
        os.mkdir(dir_path)
    
    def _download_tables(self, domains, elm_name, elm_dir):
        print(f'текущие домайны: {domains[elm_name]}')
        for domain_name in domains[elm_name]:
            api = UnionAPI(domain_name)
            full_file_path = os.path.join(elm_dir, f'{domain_name}.tsv')
            api.write_to_file(full_file_path)

    def download_proteins_sequence_data(self, sequence_id):
        root_dir = os.path.join(self.folder_path, sequence_id)
        self._build_dir_if_not_exist(root_dir)
        elm_head, elm_table = get_elm_table(sequence_id)

        domains = get_all_domains()
        processed_proteins_set = set()
        for row in elm_table:
            elm_name = row[0]
            elm_dir = os.path.join(root_dir, elm_name)
            self._build_dir_if_not_exist(elm_dir)
            if elm_name not in processed_proteins_set and elm_name in domains.keys():
                self._download_tables(domains, elm_name, elm_dir)
            processed_proteins_set.add(elm_name)
            print(processed_proteins_set)
            
if __name__ == '__main__':
    loader = ProteinsSquenceDownloader('C:/Users/andre/OneDrive/Desktop/interProScript/proteins_scripts')
    loader.download_proteins_sequence_data('RB1_human')
    # api = UnionAPI('PF00017')
    # for protein in api.get_protein_and_gene():
    #     print(protein)
    #     print(api.downloaded_proteins_count)
    #     print(api.proteins_downloaded_persent)