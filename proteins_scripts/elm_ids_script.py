BASE_URL_BEGIN = 'http://elm.eu.org/cgimodel.py?fun=Submit&swissprotId='
import requests
from bs4 import BeautifulSoup, ResultSet, Tag

#поработать над названиями
#упихать url-ы в конфиги
#перейти везде на ООП???
#сделать код надежнее(особенно при сборе правильного url), мб циклы или try/except

class FinishUrlGetter:

    def _build_finish_url(self, soup: BeautifulSoup):
        url_tags = soup.find_all(attrs={
            'content':lambda content: not(content is None) and 'URL=' in content 
        })
        url_tag = url_tags[0]
        url_mata_txt:str = url_tag['content']
        url_from_meta = url_mata_txt[url_mata_txt.index('URL=')+4:]
        return f'http://elm.eu.org/{url_from_meta}'

    def get_finish_url_from_medium_url(self, medium_url):
        res = requests.get(medium_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        finish_url = self._build_finish_url(soup)
        return finish_url

class ProteinsElmNameGetter:
    '''
    - просматривает и забирает со страницы сайта elm.org нужные протеины
    - основной метод выдает список протеинов для определенной последовательности(например, для EPN1_HUMAN)
    '''
    def _is_table_with_body_parent(self, tag: Tag):
        if tag.name == 'table':
            return tag.parent.name == 'body'
        return False
    
    def _retrive_right_proteins_table(self, soup:BeautifulSoup):
        body = soup.body
        tables = soup.find_all(self._is_table_with_body_parent)
        if len(tables)>3:
            if 'Results of ELM motif search after globular domain filtering' in tables[3].previous_sibling.previous_sibling.previous_sibling.previous_sibling.text:
                return tables[3]
            else:
                raise Exception(msg='no h2 with right txt')
            
        return tables[0]


    def _get_proteins_ids(self, table:Tag):
        trs_list:ResultSet[Tag] = table.tbody.find_all('tr', recursive=False)
        elm_ids: list[str] = []
        for i in range(1, len(trs_list)):
            if not trs_list[i] is None:
                tds:ResultSet[Tag] = trs_list[i].find_all('td', recursive=False)
                if len(tds)>0:
                    elm_ids.append(str(tds[0].text).replace(' ', '').replace('\n', ''))
        return elm_ids
        
    def get_elm_ids_from_elm_page(self, url):
        sequences_page = requests.get(url)
        finish_soup = BeautifulSoup(sequences_page.text, 'html5lib')
        table = self._retrive_right_proteins_table(finish_soup)
        proteins_ids = self._get_proteins_ids(table)
        return proteins_ids#начальный список протеино

def get_elm_ids_by_squence_id(sequence_id):
    '''
    - внешний интерфейс
    - на вход: id последовательности протеинов, например EPN1_HUMAN
    - выдает все качественные протеины, которые входят в эту последовательность
    '''
    finish_url_getter = FinishUrlGetter()
    proteins_getter = ProteinsElmNameGetter()
    finish_url = finish_url_getter.get_finish_url_from_medium_url(f'{BASE_URL_BEGIN}{sequence_id}')
    return proteins_getter.get_elm_ids_from_elm_page(finish_url)