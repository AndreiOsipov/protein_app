import requests
import logging


URL_BEGIN = f'https://rest.uniprot.org/uniprotkb/search?query=accession:'

class GenesGetter:
    def __init__(self) -> None:
        self.logger:logging.Logger = logging.getLogger(name="uniprot_script_logger")
        self.logger_handler = logging.FileHandler(filename=f'{__name__}.log', mode='a')
        self.logger_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
        self.logger_handler.setFormatter(self.logger_formatter)
        self.logger.addHandler(self.logger_handler)
    
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
                self.logger.log(level=logging.ERROR,msg=f'error, acces_id: {acces_id}')
                return []
        return []