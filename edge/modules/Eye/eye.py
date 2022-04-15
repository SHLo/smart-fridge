import cv2
import json
from azure.iot.device import Message
import asyncio
import logging
import cv

logger = logging.getLogger('__name__')

async def snap(client):
    cap = cv2.VideoCapture(0)
    _, img = cap.read()
    cap.release()

    result = cv.inference_general(img)

    if not result:
        return

    script = dict_to_script(result)
    await speak(script, client)


def dict_to_script(result_dict):
    return ', '.join([f'{count} {object_type}' for object_type, count in result_dict.items()])


async def speak(text, client):
    await client.send_message_to_output(Message(json.dumps(
        {'text': text}), content_encoding='utf-8', content_type='application/json'), 'mouth')
    await asyncio.sleep(5)

