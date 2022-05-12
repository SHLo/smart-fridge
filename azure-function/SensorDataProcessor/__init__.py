import json
import logging
import base64
from . import db
from . import reminder

import azure.functions as func


def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    data = event.get_json()

    device_id = data['systemProperties']['iothub-connection-device-id']
    category = device_id
    body = json.loads(base64.b64decode(data['body']).decode('utf-8'))

    for zone, value in body.items():
        position = f'{category}-{zone}'
        isFresh = True

        if value > db.category_table[category]['gasThreshold']:
            isFresh = False
            reminder.remind(position)
        
        logging.info(f'update gas value of {position} to {value}, {isFresh}')
        
        db.update_gas_value(position, value, isFresh)


    logging.info('Python EventGrid trigger processed an event: %s', result)
