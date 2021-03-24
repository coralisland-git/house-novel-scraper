import requests
from lxml import etree
import json
import pdb
from base import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from pyvirtualdisplay import Display
display = Display(visible=0, size=(1600, 1200))
display.start()

class Rchs_pastperfectonline_com:
    name = 'rchs_pastperfectonline_com'
    base_url = 'https://rchs.pastperfectonline.com'
    delay_time = 10

    def __init__(self):
        self.db, self.cursor = connect_mysql_db()
        self.session = requests.Session()
        options = Options()
        # self.driver = webdriver.Chrome('./chromedriver.exe', options=options)
        self.driver = webdriver.Chrome(options=options)
        self.start_requests()        
    
    def start_requests(self):
        try:
            page_num = 1
            while True:
                url = f'https://rchs.pastperfectonline.com/search?page={page_num}&search_criteria=house'
                self.driver.get(url)
                tree = etree.HTML(self.driver.page_source)
                try:
                    WebDriverWait(self.driver, self.delay_time).until(EC.presence_of_element_located((By.XPATH, '//div[@class="indvResultDetails"]')))
                except:
                    pass
                collections = eliminate_space(tree.xpath('.//div[@class="indvResultDetails"]//h1//a/@href'))
                if collections == []:
                    break
                for c_url in collections:
                    c_url = f'{self.base_url}{c_url}'
                    self.parse_collection(c_url)
                page_num += 1
        except Exception as e:
            print(e)
    
    def parse_collection(self, c_url):
        try:
            self.driver.get(c_url)
            try:
                WebDriverWait(self.driver, self.delay_time).until(EC.presence_of_element_located((By.XPATH, '//table[@class="interiorResultTable"]')))
            except:
                pass
            c_id = eliminate_space(c_url.split('/'))[-1]
            c_tree = etree.HTML(self.driver.page_source)
            fields = c_tree.xpath('.//table[@class="interiorResultTable"]//tr')            
            data = {}
            for field in fields:
                key = validate(field.xpath('.//td[@class="category"]//text()')).lower()
                value = validate(field.xpath('.//td[@class="display"]//text()'))
                if key == 'description':
                    data['caption'] = validate(value.split('caption:')[-1]).replace('"', '')
                if key == 'date':
                    data['photo_date'] = validate(value.split(' ')[0])
                if key == 'subjects':
                    data['subject'] = value
                if key == 'notes':
                    data['public_history'] = value
                if key == 'catalog number':
                    data['national_register_of_historic_places'] = value

            data['photo_decade'] = ''
            data['user_comments'] = ''
            data['source'] = 'Ramsey County Historical Society'
            data['city'] = 'St. Paul'
            data['state'] = 'Minnesota'
            data['street_address'] = ''
            data['uuid'] = generate_uuid(f'rchs_{c_id}')
            photo_urls = eliminate_space(c_tree.xpath('.//div[contains(@class, "largeImage")]//img/@src'))
            if len(photo_urls) > 0:
                data['photo_url'] = photo_urls[0]
                data['photo_location'] = f"photos/{self.name}/{c_id}.jpg"
                download_photo(self.session, data['photo_url'], {}, f"photos/{self.name}", data['photo_location'])

            insert_data_into_mysql_db(self.db, self.cursor, data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    Rchs_pastperfectonline_com()
