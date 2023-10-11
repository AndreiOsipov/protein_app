import requests
import logging


URL_BEGIN = f'https://rest.uniprot.org/uniprotkb/search?query=accession:'

class GenesGetter:
    def get_genes_list_by_acces_id(self, acces_id:str):
        '''
        - выдает список генов в которых встречается данный протеин
        '''
        url = URL_BEGIN + acces_id + '&fields=gene_names&format=json'
        res = requests.get(url)
        
        entry = res.json()['results'][0]
        
        if 'genes' in entry:
            try:
                return [str(gene['geneName']['value']) for gene in entry['genes'] if 'geneName' in gene]
            except:
                # logger = 
                # logger.log(level=logging.ERROR,msg=f'error, acces_id: {acces_id}')
                return []
        return []