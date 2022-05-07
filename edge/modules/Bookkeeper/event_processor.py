import logging
import datetime
import db
from azure.iot.device import Message
import asyncio
import json


logger = logging.getLogger('__name__')

now = datetime.datetime.now()

last_items_detected = {'ts': now}
last_pressure_event = {'ts': now}

# logger.warning(f'{db.category_table}')

async def process(input_name, data, client):
    logger.warning(f'event comes from {input_name}: {data}')

    if input_name == 'tray':
        if data['event_type'] == 'gas':
            await process_gas(data['payload'], client)

        if data['event_type'] == 'pressure_change':
            process_pressure_change(data['payload'])
    
    if input_name == 'eye':
        if data['event_type'] == 'items':
            process_items(data['payload'])


async def process_gas(payload, client):
    for position, value in payload.items():
        category, _ = position.split('-')

        isFresh = True

        if value > db.category_table[category]['gasThreshold']:
            isFresh = False
            await speak(f'food in {position} has become stale', client)
            
        logger.warning(f'update gas value of {position} to {value}')
        db.update_gas_value(position, value, isFresh)


async def speak(text, client):
    await client.send_message_to_output(Message(json.dumps(
        {'text': text}), content_encoding='utf-8', content_type='application/json'), 'mouth')
    await asyncio.sleep(5)


def process_pressure_change(payload):
    if payload['change_type'] != 'increase':
        return

    now = datetime.datetime.now()
    last_pressure_event['ts'] = now
    last_pressure_event['payload'] = payload


def process_items(payload):
    now = datetime.datetime.now()
    last_items_detected['ts'] = now
    last_items_detected['payload'] = payload
    
    logger.warning(f'add items into DB: {payload}')

    for category in payload:
        # db.update_count(category, 1)
        db.insert_item(category, last_pressure_event['payload']['current_weight'] / 100.0)