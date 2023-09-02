import requests

URL_BEGIN = f'https://rest.uniprot.org/uniprotkb/search?query=accession:'

def get_genes_list_by_acces_id(acces_id:str):
    url = URL_BEGIN + acces_id + '&fields=gene_names&format=json'
    res = requests.get(url)
    
    entry = res.json()['results'][0]
    if 'genes' in entry:
        return [str(gene['geneName']['value']) for gene in entry['genes']]
    return []