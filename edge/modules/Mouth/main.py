# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
import mouth
import json
import logging
from azure.iot.device.aio import IoTHubModuleClient
from collections import deque

logger = logging.getLogger('__name__')

# Event indicating client stop
stop_event = threading.Event()

speech_queue = deque()


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to 'input1'.
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == 'script':
            logger.warning('the data in the message received on script was ')
            logger.warning(message.data)
            logger.warning('custom properties are')
            logger.warning(message.custom_properties)
            text = json.loads(message.data)['text']
            speech_queue.append(text)

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
        if speech_queue:
            text = speech_queue.popleft()
            mouth.speak(text)


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
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == '__main__':
    main()
