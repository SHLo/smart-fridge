import os
from unicodedata import category
import azure.cosmos.cosmos_client as cosmos_client
import datetime
import logging

DB_HOST = os.getenv('DB_HOST')
DB_KEY = os.getenv('DB_KEY')
DATABASE_ID = os.getenv('DATABASE_ID')
CATEGORIES_CONTAINER_ID = os.getenv('CATEGORIES_CONTAINER_ID')
WAREHOUSE_CONTAINER_ID = os.getenv('WAREHOUSE_CONTAINER_ID')
IOTEDGE_MODULEID = os.getenv('IOTEDGE_MODULEID')

logger = logging.getLogger('__name__')
db_client = cosmos_client.CosmosClient(
    DB_HOST, {'masterKey': DB_KEY}, user_agent=IOTEDGE_MODULEID, user_agent_overwrite=True)
db = db_client.get_database_client(DATABASE_ID)
categories_container = db.get_container_client(CATEGORIES_CONTAINER_ID)
warehouse_container = db.get_container_client(WAREHOUSE_CONTAINER_ID)


def get_categories():
    query = f'SELECT * FROM {CATEGORIES_CONTAINER_ID}'

    try:
        items = categories_container.query_items(
            query=query, enable_cross_partition_query=True)

        return items
    
    except:
        return []


def get_position(position):
    query = f'SELECT * FROM {WAREHOUSE_CONTAINER_ID} WHERE {WAREHOUSE_CONTAINER_ID}.position = "{position}"'

    try:
        item = warehouse_container.query_items(
            query=query, enable_cross_partition_query=True).next()

        return item
    
    except:
        return {}


def update_gas_value(position, value, is_fresh):
    item = get_position(position)

    if not item:
        return

    item['gasValue'] = value
    item['isFresh'] = is_fresh
    
    warehouse_container.replace_item(item=item, body=item)


def get_avail_position(category):
    query = f'SELECT * FROM {WAREHOUSE_CONTAINER_ID} WHERE {WAREHOUSE_CONTAINER_ID}.category = "{category}" AND {WAREHOUSE_CONTAINER_ID}.weight = 0'

    try:
        item = warehouse_container.query_items(
            query=query, enable_cross_partition_query=True).next()

        return item
    
    except:
        return {}


def insert_item(category, weight):
    item = get_avail_position(category)

    if not item:
        return

    now = datetime.datetime.now()

    item['weight'] = weight
    
    item['itemId'] = f'{category}-{now.strftime("%Y%m%d%H%M%S")}'
    item['inTime'] = now.strftime('%Y-%m-%d %H:%M:%S')
    item['allergy'] = category_table[category]['allergy']
    
    warehouse_container.replace_item(item=item, body=item)


categories = get_categories()
category_table = {}

for category in categories:
    category_name = category['category']
    category_table[category_name] = category