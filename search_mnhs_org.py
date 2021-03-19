import requests
from lxml import etree
import json
import pdb
import re
from base import *


class Search_mnhs_org:
    name = 'search_mnhs_org'
    base_url = 'https://search.mnhs.org'

    def __init__(self):
        self.db, self.cursor = connect_mysql_db()
        self.session = requests.Session()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cookie': '_ga=GA1.2.2127827836.1615311398; _gid=GA1.2.1680323628.1615422977; _gat=1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        }
        self.start_requests()
    
    def start_requests(self):
        try:
            page_num = 1
            while True:
                url = f'https://search.mnhs.org/index.php?collection[]=mn_mhs-cms&subject[]=Residences&count=100&startindex={page_num}'
                response = self.session.get(url, headers=self.headers)
                tree = etree.HTML(response.text)
                collections = tree.xpath('//div[@id="main-content"]//span[@class="list_right"]//strong[@class="item-title"]//a')
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
            data = {}
            fields = c_tree.xpath('.//table[@id="itemTable"]//tr')
            for field in fields:
                key = validate(field.xpath('.//th//text()')).lower()
                value = validate(field.xpath('.//td//text()'))
                if key == 'description':
                    data['caption'] = value
                if key == 'subjects':
                    data['subject'] = value
                if key == 'dates':
                    years = re.findall('(\d{4})', value)
                    if len(years) > 0:
                        data['year_built'] = years[0]
                if key == 'creation':
                    data['photo_publisher'] = eliminate_space(value.split(':'))[-1]
                if key == 'places':
                    values = field.xpath('.//td//text()')
                    try:
                        addrs = values[0].split(':')[-1].split(', ')
                        if len(addrs) == 5:
                            addr, data['city'], data['county'], data['state'], country = addrs                            
                            if 'neighborhood' in addr.lower():
                                data['neighborhood'] = addr
                            else:
                                data['street_address'] = addr
                        else:
                            data['city'], data['county'], data['state'], country = addrs
                    except:
                        pass

            thumbnail_url = validate(c_tree.xpath('.//div[@class="item-group"]//img/@src'))
            if thumbnail_url != '':
                data['thumbnail_url'] = f'http://collections.mnhs.org/cms/{thumbnail_url}'
            data['source'] = 'Search the Minnesota Historical Society'
            data['source_url'] = c_url            
            c_id = c_url.split('?irn=')[1].split('&')[0]
            data['uuid'] = generate_uuid(f"mnhs_{c_id}")
            # download_photo(self.session, data['photo_url'], {}, f"photos/{self.name}", data['photo_location'])

            insert_data_into_mysql_db(self.db, self.cursor, data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    Search_mnhs_org()
