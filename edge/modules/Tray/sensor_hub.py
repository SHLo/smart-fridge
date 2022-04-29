# Importing Libraries
import serial
import time
import json
import asyncio
import logging
import threading

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=.1)
sensor_data = {}
logger = logging.getLogger('__name__')

def ser_read():
    arduino.write(bytes('r', 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline().decode('utf-8')
    if not data:
        return
    data = json.loads(data)
    for k, v in data.items():
        sensor_data[k] = v
    logger.warning(sensor_data)
    

def read_pressure():
    return sensor_data.get('pressure', 0)

def read_gas():
    ret = {}
    for k, v in sensor_data.items():
        if k == 'pressure':
            continue
        ret[k] = v
    return ret

async def loop(): 
    while True:
        await ser_read()
        await asyncio.sleep(0.5)


class SensorThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        while True:
            ser_read()

sensor_thread = SensorThread()
sensor_thread.start()