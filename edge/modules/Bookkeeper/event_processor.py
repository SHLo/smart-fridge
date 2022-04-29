import logging
import datetime
import db

logger = logging.getLogger('__name__')

now = datetime.datetime.now()

last_items_detected = {'ts': now}
last_pressure_event = {'ts': now}

def process(input_name, data):
    logger.warning(f'event comes from {input_name}: {data}')

    if input_name == 'tray':
        if data['event_type'] == 'gas':
            process_gas(data['payload'])

        if data['event_type'] == 'pressure_change':
            process_pressure_change(data['payload'])
    
    if input_name == 'eye':
        if data['event_type'] == 'items':
            process_items(data['payload'])


def process_gas(payload):
    for category, value in payload.items():
        logger.warning(f'update gas value of {category} to {value}')
        db.update_gas_value(category, value)


def process_pressure_change(payload):
    now = datetime.datetime.now()
    last_pressure_event['ts'] = now
    last_pressure_event['payload'] = payload

    if payload == 'increase':
        if (now - last_items_detected['ts']).total_seconds() > 5:
            return
        
        items = last_items_detected.get('payload')
        if not items:
            return
        
        logger.warning(f'add items into DB: {items}')

        for category in items:
            db.update_count(category, 1)


def process_items(payload):
    now = datetime.datetime.now()
    last_items_detected['ts'] = now
    last_items_detected['payload'] = payload
    
    if last_pressure_event.get('payload', '') != 'decrease':
        return
    
    if (now - last_pressure_event['ts']).total_seconds() > 5:
        return
    
    logger.warning(f'subtract items into DB: {payload}')

    for category in payload:
        db.update_count(category, -1)