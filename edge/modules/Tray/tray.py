import pressure_reader
import asyncio
import os
import json
import logging
import sensor_hub
from azure.iot.device import Message

PRESSURE_THRESHOLD = int(os.environ['PRESSURE_THRESHOLD'])
GAS_MONITORING_PERIOD = int(os.environ['GAS_MONITORING_PERIOD'])
logger = logging.getLogger('__name__')

async def pressure_event_monitor(client):
    last_pressure = 0
    counter = 0
    gas_data = {'event_type': 'gas', 'payload': None}
    pressure_data = {'event_type': 'pressure_change', 'payload': None}

    while True:
        # pressure = pressure_reader.readadc()
        pressure = sensor_hub.read_pressure()
        logger.warning(f'pressure: {pressure}')
        pressure_diff = pressure - last_pressure
        if pressure_diff > PRESSURE_THRESHOLD:
            pressure_data['payload'] = 'increase'
            await bookkeeping(pressure_data, client)
        
        if pressure_diff < -PRESSURE_THRESHOLD:
            pressure_data['payload'] = 'decrease'
            await bookkeeping(pressure_data, client)

        last_pressure = pressure

        counter += 1
        if counter == GAS_MONITORING_PERIOD:
            gas = sensor_hub.read_gas()
            gas_data['payload'] = gas
            await bookkeeping(gas_data, client)
            counter = 0

        await asyncio.sleep(1)

async def bookkeeping(data, client):
    logger.warning(f'event data: {data}')
    await client.send_message_to_output(Message(json.dumps(data), content_encoding='utf-8', content_type='application/json'), 'bookkeeper')
    if data['event_type'] == 'pressure_change':
        await asyncio.sleep(3)
        
