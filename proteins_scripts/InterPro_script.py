# standard library modules
import json, ssl
# from urllib import request
# from urllib.error import HTTPError
import requests
from time import sleep
import time
from dataclasses import dataclass
BASE_URL = "https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/pfam/"
NO_PFAM_BASE_URL = 'https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/InterPro/'

@dataclass
class Protein:
  accession: str
  source_database: str
  name: str
  taxId: str
  scientificName: str
  length: int
  entries_accession: str
  entry_protein_locations: str

class DomainDictParser:
  def parse_items(self, items):
    if type(items)==list:
      return ",".join(items)
    return ""

  def parse_member_databases(self, dbs):
    if type(dbs)==dict:
      return ";".join([f"{db}:{','.join(dbs[db])}" for db in dbs.keys()])
    return ""

  def parse_go_terms(self, gos):
    if type(gos)==list:
      return ",".join([go["identifier"] for go in gos])
    return ""

  def parse_locations(self, entries):
    if type(entries)==list:
      
      return ",".join([",".join(
        [",".join([f"{fragment['start']}..{fragment['end']}" for fragment in location["fragments"]])
        for location in entry['entry_protein_locations']])
        for entry in entries])
    return ""

  def parse_group_column(self, values, selector):
    return ",".join([self.parse_column(value, selector) for value in values])

  def parse_column(self, value, selector):
    if value is None:
      return ""
    elif "member_databases" in selector:
      return self.parse_member_databases(value)
    elif "go_terms" in selector: 
      return self.parse_go_terms(value)
    elif "children" in selector: 
      return self.parse_items(value)
    elif "locations" in selector:
      return self.parse_locations(value)
    return str(value)

class InterProConnect:
  '''
  - представляет собой единицу подключения к сайту InterPro по принципу определенного домайна
  - для домайна (например PF00017) находит все протеины, которые по нему взаимодействуют
  '''
  #TODO логированние методов _get_page_answer, _get_domain_json_answer, _build_proteins_list, output_list
  #TODO добавить timeout
  def _get_page_answer(self, url):
    #TODO залогировать и добавить timeout
    attepmt_number = 1
    while True:
      print(f'url = {url}')
      try:
          answer = requests.get(url, headers={"Accept": "application/json"})
          json_answer:dict = answer.json()
          return answer.status_code, json_answer
      except:
        if attepmt_number < 3:
          time.sleep(5)
          continue
        else:
          return None, None
        
  def _get_domain_json_answer(self, urls):
      for url in urls:
        code, domain_info_dict = self._get_page_answer(url)
        if code == 200:
          return domain_info_dict
        
  def _build_proteins_list(self):
    proteins_lst:list[Protein] = []
    column_parser = DomainDictParser()
    for item in self.proteins_answer["results"]:
      proteins_lst.append(Protein(
        column_parser.parse_column(item["metadata"]["accession"], 'metadata.accession'),
        column_parser.parse_column(item["metadata"]["source_database"], 'metadata.source_database'),
        column_parser.parse_column(item["metadata"]["name"], 'metadata.name'),
        column_parser.parse_column(item["metadata"]["source_organism"]["taxId"], 'metadata.source_organism.taxId'),
        column_parser.parse_column(item["metadata"]["source_organism"]["scientificName"], 'metadata.source_organism.scientificName'),
        column_parser.parse_column(item["metadata"]["length"], 'metadata.length'),
        column_parser.parse_column(item["entries"][0]["accession"], 'entries[0].accession'),
        column_parser.parse_column(item["entries"], 'entries[0].entry_protein_locations')
      ))
    return proteins_lst
  
  def __init__(self, domain_name: str, test = False) -> None:
    #TODO залогировать exception
    self.test = test
    self.context = ssl._create_unverified_context()
    self.domain_name = domain_name
    self.url = BASE_URL + self.domain_name +'/taxonomy/uniprot/9606/?page_size=20'
    self.no_pfam_url = NO_PFAM_BASE_URL + self.domain_name +'/taxonomy/uniprot/9606/?page_size=20'
    
    try:
      self.proteins_answer = self._get_domain_json_answer([self.url, self.no_pfam_url])
      self.proteins_count = self.proteins_answer["count"] 
      self.next_url = self.proteins_answer["next"]
    except:
      raise Exception(f"wrong domain: {self.domain_name}")

  def output_list(self):
    '''
    - выдает елдом список протеинов, которые взаимодействубт по определенному домайну
    '''
    yield self._build_proteins_list()
    sleep(1)
    if not self.test:
      while self.next_url:    
        code, self.proteins_answer = self._get_page_answer(self.next_url)
        self.next_url = self.proteins_answer["next"]
        yield self._build_proteins_list()
        if self.next_url:
          sleep(1)

if __name__ == "__main__":
  page_connect = InterProConnect('PF00149')
  for lst in page_connect.output_list():
    print(lst)
    