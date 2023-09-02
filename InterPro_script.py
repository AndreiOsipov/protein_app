# standard library modules
import sys, errno, re, json, ssl
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


def get_page_answer(url, context):
  attepmt_number = 1
  while True:
    try:
        req = request.Request(url, headers={"Accept": "application/json"})
        res = request.urlopen(req, context=context)
        
        if res.status != 200:
          return res.status, None
        return res.status, json.loads(res.read().decode())
    except HTTPError as error:
      if error.code == 408:
        return error.code, None
      if attepmt_number < 3:
        time.sleep(5)
        continue
      raise HTTPError('url', code=error.code, msg='errror during get page')
       
def output_list(domain: str):
  
  #разбить на подключение и вытаскивание данных
  #добавить входной аргумент -- id домена, чьи белки ищем
  #рассмотреть возможность использования yeld
  
  #disable SSL verification to avoid config issues
  context = ssl._create_unverified_context()

  next = BASE_URL + domain +'/taxonomy/uniprot/9606/?page_size=200'
  last_page = False

  
  attempts = 0

  
  while next:
    proteins_lst:list[Protein] = []
    code, proteins = get_page_answer(next,context)
    
    if proteins:
      next = proteins["next"]
    
    elif code == 204:
        #no data so leave loop
        break
    else:
      time.sleep(61)
      continue

    for item in proteins['results']:
      
      proteins_lst.append(
          Protein(
            parse_column(item["metadata"]["accession"], 'metadata.accession'),
            parse_column(item["metadata"]["source_database"], 'metadata.source_database'),
            parse_column(item["metadata"]["name"], 'metadata.name'),
            parse_column(item["metadata"]["source_organism"]["taxId"], 'metadata.source_organism.taxId'),
            parse_column(item["metadata"]["source_organism"]["scientificName"], 'metadata.source_organism.scientificName'),
            parse_column(item["metadata"]["length"], 'metadata.length'),
            parse_column(item["entries"][0]["accession"], 'entries[0].accession'),
            parse_column(item["entries"], 'entries[0].entry_protein_locations')
      ))

    yield proteins_lst
    
    # Don't overload the server, give it time before asking for more
    if next:
      sleep(1)

if __name__ == "__main__":
  for lst in output_list():
    print(lst)
