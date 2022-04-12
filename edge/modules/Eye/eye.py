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

    results = cv.inference(img)
    

    