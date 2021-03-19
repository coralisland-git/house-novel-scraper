import requests
from lxml import etree
import json
import pdb
from base import *


class Duluthpreservation_org:
    name = 'duluthpreservation_org'
    base_url = 'https://duluthpreservation.org'

    def __init__(self):
        self.db, self.cursor = connect_mysql_db()
        self.session = requests.Session()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cookie': '_ga=GA1.2.1669558988.1616052027; _gid=GA1.2.677540328.1616052027',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }
        self.start_requests()
    
    def start_requests(self):
        try:            
            url = 'https://duluthpreservation.org/property/'
            response = self.session.get(url, headers=self.headers)
            tree = etree.HTML(response.text)
            collections = tree.xpath('.//article')            
            for collection in collections:
                self.parse_collection(collection)            
        except Exception as e:
            print(e)
    
    def parse_collection(self, collection):
        try:
            c_url = validate(collection.xpath('.//a[@class="big-link"]/@href'))
            c_id = eliminate_space(c_url.split('/'))[-1].replace('-', '_')
            c_response = self.session.get(c_url, headers=self.headers)
            c_tree = etree.HTML(c_response.text)
            data = {}
            data['caption'] = validate(c_tree.xpath('.//div[@class="entry-content"]/p//text()'))
            data['source'] = 'Duluth Preservation Alliance'
            data['source_url'] = c_url
            year_and_sub = eliminate_space(validate(collection.xpath('.//small//text()')).replace(',', '').split('|'))
            if len(year_and_sub) > 0:
                data['year_built'] = year_and_sub[0]
            if len(year_and_sub) > 1:                
                data['subject'] = year_and_sub[1]
            data['city'] = 'Duluth'
            data['state'] = 'Minnesota'
            data['street_address'] = validate(c_tree.xpath('.//h1[@class="entry-title"]//text()'))
            
            data['uuid'] = generate_uuid(f'dpa_{c_id}')
            photo_url = validate(c_tree.xpath('.//div[@id="header-image"]//img/@src'))
            if photo_url != '':
                data['photo_url'] = f'{self.base_url}{photo_url}'
                data['photo_location'] = f"photos/{self.name}/{c_id}.jpg"
                download_photo(self.session, data['photo_url'], {}, f"photos/{self.name}", data['photo_location'])

            insert_data_into_mysql_db(self.db, self.cursor, data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    Duluthpreservation_org()
