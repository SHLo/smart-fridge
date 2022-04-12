import cv2
import os
from pathlib import Path

VIDEO_FOLDER = './artifacts/video'
IMAGE_FOLDER = './artifacts/images'

video_files = os.listdir(VIDEO_FOLDER)

for video_file in video_files:
    video_path = os.path.join(VIDEO_FOLDER, video_file)
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    success, _ = vidcap.read()

    if not success:
        raise Exception(f'read video {video_path} failed!')

    print(f'Read video {video_path} SUCESSFULLY. The fps of the video is {fps}')

    image_folder = os.path.join(IMAGE_FOLDER, Path(video_path).stem)
    os.makedirs(image_folder)

    frames = 0

    while True:
        success, img = vidcap.read()
        if not success:
            break

        cv2.imwrite(os.path.join(image_folder , f'frame_{frames}.jpg'), img)
        frames += 1
    
    print(f'Finish extracting video {video_path}')





