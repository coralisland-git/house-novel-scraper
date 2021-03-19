import requests
from lxml import etree
import json
import pdb
from base import *


class Stillwater_mn_org:
    name = 'stillwater_mn_org'
    base_url = 'http://www.stillwater-mn.org'

    def __init__(self):
        self.db, self.cursor = connect_mysql_db()
        self.session = requests.Session()
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cookie': '__utma=210936151.1289818544.1615623771.1615623771.1615623771.1; __utmz=210936151.1615623771.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.start_requests()
    
    def start_requests(self):
        try:
            url = 'http://www.stillwater-mn.org/hpc/api/ListWebPropertyAddresses?sort=&group=&filter='
            response = self.session.get(url, headers=self.headers)
            collections = json.loads(response.text).get('Data', [])
            for collection in collections[:1]:
                self.parse_collection(collection)
        except Exception as e:
            print(e)
    
    def parse_collection(self, collection):
        try:
            c_id = collection.get('PIN')
            c_url = f"http://www.stillwater-mn.org/hpc/Property/{c_id}"
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Cookie': '__utma=210936151.1289818544.1615623771.1615623771.1615623771.1; __utmz=210936151.1615623771.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }
            c_response = self.session.get(c_url, headers=headers)
            c_tree = etree.HTML(c_response.text)
            data = {}
            data['caption'] = validate(c_tree.xpath('.//p[@class="lead"]//text()'))
            data['source'] = 'Heirloom Homes and Landmark'
            data['subject'] = validate(collection.get('PropertyName', ''))
            data['city'] = 'City of Stillwater'
            data['state'] = 'Minnesota'            
            data['neighborhood'] = validate(collection.get('NeighborhoodName', ''))
            data['street_address'] = validate(collection.get('FullAddress', ''))
            fields = c_tree.xpath('.//div[@class="row featurette"]')[-1].xpath('./div/p')
            for field in fields:
                key = validate(field.xpath('.//span[@class="property-field"]//text()')).lower()                
                if 'construction date' in key:
                    data['year_built'] = validate(field.xpath('.//span[@class="property-value"]//text()'))
                if 'state historic preservation office inventory number' in key:
                    data['national_register_of_historic _places'] = validate(field.xpath('.//span[@class="property-value"]//a//@href'))
            data['uuid'] = generate_uuid(f'swmn_{c_id}')
            photo_url = validate(c_tree.xpath('.//img[@class="featurette-image img-fluid mx-auto"]/@src'))
            if photo_url != '':
                data['photo_url'] = f'{self.base_url}{photo_url}'
                data['photo_location'] = f"photos/{self.name}/{c_id}.jpg"                
                download_photo(self.session, data['photo_url'], {}, f"photos/{self.name}", data['photo_location'])

            insert_data_into_mysql_db(self.db, self.cursor, data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    Stillwater_mn_org()
