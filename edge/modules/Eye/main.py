# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
import os
from azure.iot.device.aio import IoTHubModuleClient
import base64
import logging
import eye

logger = logging.getLogger('__name__')

IOTEDGE_DEVICEID = os.getenv('IOTEDGE_DEVICEID')
IOTEDGE_MODULEID = os.getenv('IOTEDGE_MODULEID')
DB_HOST = os.getenv('DB_HOST')
DB_KEY = os.getenv('DB_KEY')
DATABASE_ID = os.getenv('DATABASE_ID')

# Event indicating client stop
stop_event = threading.Event()

busy = False

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        global busy 
        if message.input_name == "tray" and not busy:
            busy = True
            while True:
                if await eye.snap(client) is True:
                    busy = False
                    break
                await asyncio.sleep(0.3)

            # while not await eye.snap(client):
            #     await asyncio.sleep(0.3)

    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler
    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client


async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages

    while True:
        # await eye.snap(client)
        # await asyncio.sleep(0.3)
        await asyncio.sleep(1000)


def main():
    print("IoT Hub Client for Python")

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()
