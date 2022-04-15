import pressure_reader
import asyncio
import os
import json
import logging
from azure.iot.device import Message

PRESSURE_THRESHOLD = int(os.environ['PRESSURE_THRESHOLD'])
logger = logging.getLogger('__name__')

async def pressure_event_monitor(client):
    last_pressure = 0
    while True:
        pressure = pressure_reader.readadc()
        logger.warning(f'pressure: {pressure}')
        pressure_diff = pressure - last_pressure
        if pressure_diff > PRESSURE_THRESHOLD:
            await send_event('increase', client)
        
        if pressure_diff < -PRESSURE_THRESHOLD:
            await send_event('decrease', client)

        last_pressure = pressure
        await asyncio.sleep(1)


async def send_event(event, client):
    logger.warning(f'pressure event: {event}')
    await client.send_message_to_output(Message(json.dumps(
        {'event': event}), content_encoding='utf-8', content_type='application/json'), 'accountant')
    await asyncio.sleep(3)
        
