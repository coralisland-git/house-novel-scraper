import requests
from lxml import etree
import json
import pdb
from base import *


class Loc_gov:
    name = 'loc_gov'
    base_url = 'https://www.loc.gov'

    def __init__(self):
        self.db, self.cursor = connect_mysql_db()
        self.session = requests.Session()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cookie': '__cfduid=d1e6794aad34f676de1c6bb70651850d71615424416; s_fid=515CEAF5D9816030-0BE915FE6EBD9599; s_cc=true; s_vi=[CS]v1|3024B5D2B8081FD8-400008FBA39C75DA[CE]; s_sq=%5B%5BB%5D%5D; s_ptc=pt.rdr%240.01%5E%5Ept.apc%240.00%5E%5Ept.dns%240.00%5E%5Ept.tcp%240.00%5E%5Ept.req%240.01%5E%5Ept.rsp%240.00%5E%5Ept.prc%240.78%5E%5Ept.onl%240.00%5E%5Ept.tot%240.82%5E%5Ept.pfi%241',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        }
        self.start_requests()
    
    def start_requests(self):
        try:
            page_num = 1
            while True:
                url = f'https://www.loc.gov/collections/historic-american-buildings-landscapes-and-engineering-records/?c=1000&fa=online-format:image&sp={page_num}&st=list'
                response = self.session.get(url, headers=self.headers)
                tree = etree.HTML(response.text)
                collections = tree.xpath('//span[@class="item-description-title"]//a')
                if collections == []:
                    break                
                for collection in collections:
                    c_url = validate(collection.xpath('./@href'))
                    self.parse_collection(c_url)
                page_num += 1
        except Exception as e:
            print(e)
    
    def parse_collection(self, c_url):
        try:
            c_response = self.session.get(c_url, headers=self.headers)
            c_tree = etree.HTML(c_response.text)
            c_id = eliminate_space(c_url.split('/'))[-1]
            data = {}
            fields = c_tree.xpath('.//dl[@id="item-cataloged-data"]/*')
            for idx, field in enumerate(fields):                
                if field.tag == 'dt':                    
                    key = validate(field.xpath('.//text()')).lower()
                    if key == 'notes':
                        data['caption'] = validate(fields[idx+1].xpath('.//text()')).split(':')[-1]
                    if key == 'repository':
                        data['national_register_of_historic_places'] = validate(fields[idx+1].xpath('.//a/@href'))

            data['photo_url'] = validate(c_tree.xpath('.//img[@class="iconic screen-dependent-image"]/@src')).replace('p_150px.jpg', 'pv.jpg#h=814&w=1024')
            # data['source'] = validate(c_tree.xpath('.//a[@class="format-label"]//text()'))
            data['source'] = 'Library of Congress'
            data['source_url'] = c_url
            data['subject'] = validate(c_tree.xpath('.//h1//cite//text()'))
            try:
                addrs = eliminate_space(data['subject'].split(','))
                data['street_address'] = addrs[-4]
                data['city'] = addrs[-3]
                data['state'] = addrs[-1]
                data['county'] = addrs[-2]
            except:
                pass
            data['uuid'] = generate_uuid(f'loc_{c_id}')
            if data['photo_url'] != '':
                data['photo_location'] = f"photos/{self.name}/{c_id}.jpg"
                download_photo(self.session, data['photo_url'], {}, f"photos/{self.name}", data['photo_location'])
            insert_data_into_mysql_db(self.db, self.cursor, data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    Loc_gov()
