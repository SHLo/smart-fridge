import logging
import datetime

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
    pass

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


def process_items(payload):
    now = datetime.datetime.now()
    last_items_detected['ts'] = now
    last_items_detected['payload'] = payload
    
    if last_pressure_event.get('payload', '') != 'decrease':
        return
    
    if (now - last_pressure_event['ts']).total_seconds() > 5:
        return
    
    logger.warning(f'subtract items into DB: {payload}')



    

