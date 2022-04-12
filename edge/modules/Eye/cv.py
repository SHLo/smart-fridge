from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import os
import logging
import io
import cv2

CV_PREDICTION_KEY = os.environ['CV_PREDICTION_KEY']
CV_ENDPOINT = os.environ['CV_ENDPOINT']
CV_PROJECT_ID = os.environ['CV_PROJECT_ID']
CV_PUBLISHED_NAME = 'Iteration4'

credentials = ApiKeyCredentials(in_headers={'Prediction-key': CV_PREDICTION_KEY})
predictor = CustomVisionPredictionClient(endpoint=CV_ENDPOINT, credentials=credentials)
logger = logging.getLogger('__name__')

def inference(img):
    _, img = cv2.imencode('.jpg', img)

    with open('./snap.jpg', 'wb') as f:
        f.write(img)
    
    result = predictor.detect_image(CV_PROJECT_ID, CV_PUBLISHED_NAME, io.BytesIO(img))
    predictions = result.predictions

    for prediction in predictions:
        if '[Auto-Generated]' in prediction.tag_name:
            continue
        logger.warning(f'inference result: {prediction.__dict__}')
        logger.warning(f'inference bounding_box: {prediction.bounding_box.__dict__}')

    return result