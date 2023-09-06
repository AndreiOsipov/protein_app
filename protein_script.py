import uniprot_script
import csv
import math
from queue import Queue
from dataclasses import dataclass
from InterPro_script import Protein, InterProConnect
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
        for proteins_lst in self.connect.output_list():
            for protein in proteins_lst:
                genes = uniprot_script.get_genes_list_by_acces_id(protein.accession)
                yield ProteinInfo(protein, genes)
    

    def write_to_file(self, file_name: str):
        self.is_starting = True
        full_file_name = file_name
        try:
            with open(full_file_name, 'at') as file:
                writer = csv.writer(file, delimiter='\t', lineterminator='\n')
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
        except:
            raise Exception(message='exception ')
        self.is_starting = False
        
if __name__ == '__main__':
    api = UnionAPI('PF00017')
    for protein in api.get_protein_and_gene():
        print(protein)
        print(api.downloaded_proteins_count)
        print(api.proteins_downloaded_persent)