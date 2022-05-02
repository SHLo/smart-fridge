from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import ApiKeyCredentials
from msrest.authentication import CognitiveServicesCredentials
import os
import logging
import io
import cv2
import collections


CV_PREDICTION_KEY = os.environ['CV_PREDICTION_KEY']
CV_ENDPOINT = os.environ['CV_ENDPOINT']
CV_PROJECT_ID = os.environ['CV_PROJECT_ID']
CV_PUBLISHED_NAME = os.environ['CV_PUBLISHED_NAME']
COG_SRV_ENDPOINT = os.environ['COG_SRV_ENDPOINT']
COG_SRV_KEY = os.environ['COG_SRV_KEY']
RECOGNIZED_TYPES = os.environ['RECOGNIZED_TYPES']

credentials = ApiKeyCredentials(in_headers={'Prediction-key': CV_PREDICTION_KEY})
predictor = CustomVisionPredictionClient(endpoint=CV_ENDPOINT, credentials=credentials)
recognized_types = set([s.strip().lower() for s in RECOGNIZED_TYPES.split(',')])

computervision_client = ComputerVisionClient(COG_SRV_ENDPOINT, CognitiveServicesCredentials(COG_SRV_KEY))
logger = logging.getLogger('__name__')

def inference(img):
    _, img = cv2.imencode('.jpg', img)

    with open('./snap.jpg', 'wb') as f:
        f.write(img)
    
    result = predictor.detect_image(CV_PROJECT_ID, CV_PUBLISHED_NAME, io.BytesIO(img))
    predictions = result.predictions

    ret = collections.defaultdict(int)

    for prediction in predictions:
        if '[Auto-Generated]' in prediction.tag_name:
            continue
        ret[prediction.tag_name] += 1
        # logger.warning(f'inference result: {prediction.__dict__}')
        # logger.warning(f'inference bounding_box: {prediction.bounding_box.__dict__}')

    logger.warning(f'inference result: {ret}')

    return ret


def inference_class(img):
    _, img = cv2.imencode('.jpg', img)

    with open('./snap.jpg', 'wb') as f:
        f.write(img)
    
    result = predictor.classify_image(CV_PROJECT_ID, CV_PUBLISHED_NAME, io.BytesIO(img))
    predictions = result.predictions

    ret = collections.defaultdict(int)

    for prediction in predictions:
        if '[Auto-Generated]' in prediction.tag_name:
            continue
        ret[prediction.tag_name] += 1

    logger.warning(f'inference result: {ret}')

    return ret


def inference_general(img):
    _, img = cv2.imencode('.jpg', img)

    with open('./snap.jpg', 'wb') as f:
        f.write(img)
    
    result = computervision_client.detect_objects_in_stream(io.BytesIO(img))
    objects = result.objects
    ret = collections.defaultdict(int)

    for object in objects:
        object_type = object.object_property.lower()
        if object_type not in recognized_types or object.confidence < 0.3:
            continue
        
        ret[object_type] += 1

        # logger.warning(f'inference result: {object.__dict__}')

    logger.warning(f'inference result: {ret}')

    return ret