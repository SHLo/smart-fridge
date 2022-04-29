import os
import azure.cosmos.cosmos_client as cosmos_client

DB_HOST = os.getenv('DB_HOST')
DB_KEY = os.getenv('DB_KEY')
DATABASE_ID = os.getenv('DATABASE_ID')
CATEGORIES_CONTAINER_ID = os.getenv('CATEGORIES_CONTAINER_ID')
IOTEDGE_MODULEID = os.getenv('IOTEDGE_MODULEID')

db_client = cosmos_client.CosmosClient(
    DB_HOST, {'masterKey': DB_KEY}, user_agent=IOTEDGE_MODULEID, user_agent_overwrite=True)
db = db_client.get_database_client(DATABASE_ID)
container = db.get_container_client(CATEGORIES_CONTAINER_ID)


def get_category(category):
    query = f'SELECT * FROM {CATEGORIES_CONTAINER_ID} WHERE {CATEGORIES_CONTAINER_ID}.category = "{category}"'

    try:
        item = container.query_items(
            query=query, enable_cross_partition_query=True).next()

        return item
    
    except:
        return {}


def update_gas_value(category, value):
    item = get_category(category)

    if not item:
        return

    item['gasValue'] = value
    if item['gasValue'] > item['gasThreshold']:
        item['fresh'] = False
    else:
        item['fresh'] = True
    
    container.replace_item(item=item, body=item)


def update_count(category, diff):
    item = get_category(category)

    item['count'] += diff

    container.replace_item(item=item, body=item)