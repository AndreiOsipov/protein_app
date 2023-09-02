import InterPro_script
import uniprot_script
import csv

from dataclasses import dataclass
from InterPro_script import Protein



@dataclass
class ProteinInfo:
    protein: Protein
    genes:list[str]

def get_protein_and_gene(domain_name):
    for proteins_lst in InterPro_script.output_list(domain_name):
        for protein in proteins_lst:
            genes = uniprot_script.get_genes_list_by_acces_id(protein.accession)
            yield ProteinInfo(protein, genes)
 

def write_to_file(file_name: str, domain_name: str):
    full_file_name = file_name
    print(f'in func {file_name} {domain_name}')
    try:
        with open(full_file_name, 'at') as file:
            writer = csv.writer(file, delimiter='\t', lineterminator='\n')
            for protein_info in get_protein_and_gene(domain_name):
                writer.writerow([
                    protein_info.protein.accession,
                    protein_info.protein.name,
                    protein_info.protein.scientificName,
                    protein_info.protein.source_database,
                    protein_info.protein.taxId,
                    protein_info.protein.length,
                    protein_info.protein.entry_protein_locations,
                    ','.join(protein_info.genes)])
        print("OK")
        return True
    except:
        print("NOT OK")
        return False