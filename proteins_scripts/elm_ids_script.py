BASE_URL = 'http://elm.eu.org/start_search/'
import requests
#поработать над названиями
#упихать url-ы в конфиги
#перейти везде на ООП???

def get_elm_table(sequence_id):
    res = requests.get(f'{BASE_URL}/{sequence_id}.tsv')
    head, table = [], []
    content = res.text.split('\n')
    head.append(content[0].split('\t'))
    for i in range(1, len(content)):
        if content[i]!= '':
            table.append(content[i].split('\t'))
    print(f'таблица будет {len(table)}')
    return head, table[:8]