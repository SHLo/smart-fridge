# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
import json
from azure.iot.device.aio import IoTHubModuleClient
import logging
import event_processor


# Event indicating client stop
stop_event = threading.Event()

logger = logging.getLogger('__name__')


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to 'input1'.
        # Messages sent to other inputs, or to the default, will be discarded
        await event_processor.process(message.input_name, json.loads(message.data), client)

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
    await asyncio.sleep(1000)


def main():
    logger.warning('IoT Hub Client for Python')

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        logger.warning('IoTHubClient sample stopped by Edge')
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        logger.warning('Unexpected error %s ' % e)
        raise
    finally:
        logger.warning('Shutting down IoT Hub Client...')
        client.shutdown()
        loop.close()


if __name__ == '__main__':
    main()
