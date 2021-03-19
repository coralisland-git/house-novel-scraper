import requests
from lxml import etree
import json
import pdb
from base import *


class Digitalcollections_hclib_org:
    name = 'digitalcollections_hclib_org'
    base_url = 'https://digitalcollections.hclib.org/digital/collection/p17208coll13'

    def __init__(self):
        self.db, self.cursor = connect_mysql_db()
        self.session = requests.Session()
        self.headers = {
            'Accept': '*/*',
            'Cookie': '_ga=GA1.2.1093894124.1615311386; JSESSIONID=923c6838-5dcd-41c4-9a52-d27200839706; _gid=GA1.2.599487822.1615413248; PHPSESSID=08d1e5d1dd1b76c8d108ade164e0b5ed; _gat_UA550725351=1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        }        
        self.start_requests()
        disconnect_mysql_db(self.db, self.cursor)
    
    def start_requests(self):
        try:
            page_num = 1
            while True:
                url = f'https://digitalcollections.hclib.org/digital/api/search/collection/p17208coll13/searchterm/Still%20Image/field/type/mode/exact/conn/and/order/title/ad/asc/page/{page_num}/maxRecords/1000'
                response = self.session.get(url, headers=self.headers)
                collections = json.loads(response.text).get('items', [])
                if collections == []:
                    break
                for collection in collections:
                    c_url = f"https://digitalcollections.hclib.org/digital/api/collections/p17208coll13/items/{validate(collection.get('itemId'))}/false"
                    self.parse_collection(c_url)
                page_num += 1
        except Exception as e:
            print(e)
    
    def parse_collection(self, c_url):
        try:
            c_response = self.session.get(c_url, headers=self.headers)
            c_info = json.loads(c_response.text)
            data = {}
            for field in c_info.get('fields', {}):
                key = validate(field.get('key', '')).lower()                
                value = validate(field.get('value', ''))
                if key == 'subjec':
                    data['subject'] = value
                if key == 'city':
                    data['city'] = value
                if key == 'state':
                    data['state'] = value
                if key == 'countr':
                    data['country'] = value
                if key == 'addres':
                    data['street_address'] = value
                if key == 'decade':
                    data['photo_decade'] = value.replace(';', ',')
                if key == 'year':
                    data['year_built'] = value
                if key == 'neighb':
                    data['neighborhood'] = value
                if key == 'date':
                    data['photo_date'] = value
                if key == 'photog':
                    data['photo_publisher'] = value
                if key == 'collec':
                    data['source'] = value
                if key == 'reposi':
                    data['national_register_of_historic_places'] = value
                if key == 'projec':
                    data['caption'] = value

            data['source'] = 'Hennepin History Museum Collections'
            data['source_url'] = f"https://digitalcollections.hclib.org/digital/collection/p17208coll13/id/{c_info.get('id', '')}/rec/1"
            data['uuid'] = generate_uuid(f"hclib_{c_info.get('id', '')}")
            thumbnail_url = validate(c_info.get('thumbnailUri', ''))
            if thumbnail_url != '':
                data['thumbnail_url'] = f"https://digitalcollections.hclib.org/digital{thumbnail_url}"
            photo_url = validate(c_info.get('imageUri', ''))
            if photo_url != '':
                data['photo_url'] = f"https://digitalcollections.hclib.org/digital{photo_url}"
                data['photo_location'] = f"photos/{self.name}/{c_info.get('id', '')}.jpg"
                download_photo(self.session, data['photo_url'], {}, f"photos/{self.name}", data['photo_location'])
            insert_data_into_mysql_db(self.db, self.cursor, data)
        except Exception as e:
            print('parse_collection: ', e)

if __name__ == '__main__':
    Digitalcollections_hclib_org()
