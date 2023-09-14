# standard library modules
import json, ssl
from urllib import request
from urllib.error import HTTPError
from time import sleep
import time
from dataclasses import dataclass
BASE_URL = "https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/pfam/"

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

def parse_items(items):
  if type(items)==list:
    return ",".join(items)
  return ""

def parse_member_databases(dbs):
  if type(dbs)==dict:
    return ";".join([f"{db}:{','.join(dbs[db])}" for db in dbs.keys()])
  return ""

def parse_go_terms(gos):
  if type(gos)==list:
    return ",".join([go["identifier"] for go in gos])
  return ""

def parse_locations(entries):
  if type(entries)==list:
    
    return ",".join([",".join(
      [",".join([f"{fragment['start']}..{fragment['end']}" for fragment in location["fragments"]])
       for location in entry['entry_protein_locations']])
      for entry in entries])
  return ""

def parse_group_column(values, selector):
  return ",".join([parse_column(value, selector) for value in values])

def parse_column(value, selector):
  if value is None:
    return ""
  elif "member_databases" in selector:
    return parse_member_databases(value)
  elif "go_terms" in selector: 
    return parse_go_terms(value)
  elif "children" in selector: 
    return parse_items(value)
  elif "locations" in selector:
    return parse_locations(value)
  return str(value)

class InterProConnect:
  def _get_page_answer(self, url):
    attepmt_number = 1
    while True:
      try:
          req = request.Request(url, headers={"Accept": "application/json"})
          res = request.urlopen(req, context=self.context)
          if res.status != 200:
            raise HTTPError('url', code=error.code, msg='errror during get page')
          return res.status, json.loads(res.read().decode())
      except HTTPError as error:
        if error.code == 204:
          raise HTTPError(self.url, error.code, msg="no data")
        if attepmt_number < 3:
          time.sleep(5)
          continue
        raise HTTPError('url', code=error.code, msg='errror during get page')
  
  def _build_proteins_list(self):
    proteins_lst:list[Protein] = []
    for item in self.proteins_answer["results"]:
      proteins_lst.append(Protein(
        parse_column(item["metadata"]["accession"], 'metadata.accession'),
        parse_column(item["metadata"]["source_database"], 'metadata.source_database'),
        parse_column(item["metadata"]["name"], 'metadata.name'),
        parse_column(item["metadata"]["source_organism"]["taxId"], 'metadata.source_organism.taxId'),
        parse_column(item["metadata"]["source_organism"]["scientificName"], 'metadata.source_organism.scientificName'),
        parse_column(item["metadata"]["length"], 'metadata.length'),
        parse_column(item["entries"][0]["accession"], 'entries[0].accession'),
        parse_column(item["entries"], 'entries[0].entry_protein_locations')
      ))
    return proteins_lst
  
  def __init__(self, domain_name) -> None:
    self.context = ssl._create_unverified_context()
    self.domain_name = domain_name
    self.url = BASE_URL + self.domain_name +'/taxonomy/uniprot/9606/?page_size=200'
    try:
      code, self.proteins_answer  = self._get_page_answer(self.url)
      self.proteins_count = self.proteins_answer["count"] 
      self.next_url = self.proteins_answer["next"]
    except:
      ...

  def output_list(self):
    yield self._build_proteins_list()
    sleep(1)
    while self.next_url:
      code, self.proteins_answer = self._get_page_answer(self.next_url)
      self.next_url = self.proteins_answer["next"]
      yield self._build_proteins_list()
      # Don't overload the server, give it time before asking for more
      if self.next_url:
        sleep(1)

if __name__ == "__main__":
  page_connect = InterProConnect('PF00017')
  for lst in page_connect.output_list():
    print(lst)
    