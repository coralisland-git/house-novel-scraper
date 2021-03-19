import re
import os
import shutil
import pymysql
import pdb

table_name = 'collections'
fields = [
    'uuid',
    'property_photo',
    'photo_location',
    'photo_url',
    'thumbnail_url',
    'caption',
    'photo_date',
    'photo_decade',
    'display_order',
    'photo_category',
    'photo_publisher',
    'source',
    'source_url',
    'subject',
    'city',
    'state',
    'county',
    'neighborhood',
    'street_address',
    'year_built',
    'property_sqft',
    'lot_sqft',
    'bedroom',
    'bathroom',
    'sales_history',
    'sales_status',
    'user_comments',
    'public_history',
    'national_register_of_historic_places'
]

def connect_mysql_db():
    db = pymysql.connect(
        host="localhost", 
        user="root", 
        passwd="root", 
        db="house_novel"
    )
    cursor = db.cursor()
    
    _SQL = """SHOW TABLES"""
    cursor.execute(_SQL)
    results = cursor.fetchall()
    print('All existing tables: ', results) # Returned as a list of tuples
    results_list = [item[0] for item in results] 
    if table_name in results_list:
        print(table_name, 'was found!')
    else:
        print(table_name, 'was NOT found!')
        _SQL = """CREATE TABLE %s (
            id int auto_increment not null primary key,
            uuid varchar(100),
            property_photo text,
            photo_location text,
            photo_url text,
            thumbnail_url text,
            caption text,
            photo_date varchar(20),
            photo_decade varchar(20),
            display_order varchar(20),
            photo_category varchar(50),
            photo_publisher varchar(50),
            source text,
            source_url text,
            subject text,
            city varchar(30),
            state varchar(30),
            county varchar(30),
            neighborhood text,
            street_address text,
            year_built varchar(20),
            property_sqft varchar(10),
            lot_sqft varchar(10),
            bedroom varchar(10),
            bathroom varchar(10),
            sales_history text,
            sales_status text,
            user_comments text,
            public_history text,
            national_register_of_historic_places text
            );""" %table_name
        cursor.execute(_SQL)
        print(table_name, 'is created')
    return db, cursor

def insert_data_into_mysql_db(db, cursor, data):
    uuid = data.get('uuid', '')
    if uuid == '':
        return False
    try:
        # check if the collection exists. if yes -> add, no -> update
        check_query = f"select * from {table_name} where uuid='{uuid}'"
        count = cursor.execute(check_query)
        if count == 0:
            values = []
            for field in fields:
                values.append(f"'{data.get(field, '')}'")
            sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(values) });"
        else :
            values = []
            for field in fields:
                values.append(f"{field}='{data.get(field, '')}'")
            sql = f"UPDATE {table_name} SET {', '.join(values)} WHERE uuid='{uuid}';"
        print(uuid)
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print('insert_data_into_mysql_db: ', e, data)
        return False
    return True

def disconnect_mysql_db(db, cursor):
    cursor.close()
    db.close()

def validate(item):
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace("'", "`").encode('ascii','ignore').decode().strip()

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def download_photo(session, image_url, headers, file_directory, file_path):
    try:
        file_content = session.get(image_url, headers=headers, stream=True)
        if not os.path.isdir(file_directory):
            os.makedirs(file_directory)
        with open(file_path, mode='wb') as output:
            file_content.raw.decode_content = True
            shutil.copyfileobj(file_content.raw, output)
    except:
        return False
    return True

def generate_uuid(value):
    try:
        ret = re.sub('[^a-zA-Z0-9]+', '_', str(value))
        if ret[0] == '_':
            ret = ret[1:]
        if ret[-1] == '_':
            ret = ret[:-1]
        return ret
    except:
        return ''