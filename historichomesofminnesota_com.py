import requests
from lxml import etree
import json
import pdb
from base import *
import usaddress


class Historichomesofminnesota_com:
    name = 'historichomesofminnesota_com'
    base_url = 'https://historichomesofminnesota.com'

    def __init__(self):
        self.db, self.cursor = connect_mysql_db()
        self.session = requests.Session()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cookie': 'ihf_lead_capture_user_id=5468905848; ihf_session_id=4f7bce15-14d0-4ae3-adb3-dec7761fc7c2; _ga=GA1.2.1143815259.1615626562; _gid=GA1.2.774326208.1616050714            ',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }
        self.start_requests()        
    
    def start_requests(self):
        try:
            page_num = 1
            while True:
                url = f'https://historichomesofminnesota.com/page/{page_num}'
                response = self.session.get(url, headers=self.headers)
                tree = etree.HTML(response.text)
                collections = tree.xpath('.//a[@class="thumbnail-wrapper"]/@href')
                if collections == []:
                    break
                for c_url in collections:                    
                    self.parse_collection(c_url)
                page_num += 1
        except Exception as e:
            print(e)
    
    def parse_collection(self, c_url):
        try:            
            c_id = eliminate_space(c_url.split('/'))[-1].replace('-', '_')
            c_response = self.session.get(c_url, headers=self.headers)
            c_tree = etree.HTML(c_response.text)
            data = {}            
            # data['source'] = eliminate_space(c_tree.xpath('.//div[contains(@id, "post")]/h2//text()'))[0]
            data['source'] = 'Historic Homes of Minnesota'
            data['source_url'] = c_url
            data['subject'] = validate(c_tree.xpath('.//p[@class="postmetadata alt"]//a[@rel="category tag"]//text()'))
            try:
                data['street_address'] = eliminate_space(c_tree.xpath('//p[@class="wp-caption-text"]//text() | //figcaption//text()'))[0]
            except:
                pass
            data['year_built'] = ''
            
            data['uuid'] = generate_uuid(f'hhm_{c_id}')
            photo_urls = eliminate_space(c_tree.xpath('.//div[contains(@id, "post")]//img/@src'))
            if len(photo_urls) != 0:
                data['photo_url'] = photo_urls[0]
                data['photo_location'] = f"photos/{self.name}/{c_id}.jpg"                
                download_photo(self.session, data['photo_url'], {}, f"photos/{self.name}", data['photo_location'])

            insert_data_into_mysql_db(self.db, self.cursor, data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    Historichomesofminnesota_com()
