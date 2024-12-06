# TechVidvan hand Gesture Recognizer

# import necessary packages

import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import threading
from keras.models import load_model
import requests
from datetime import datetime
from google.cloud import storage

import math
import torchvision.transforms as transforms
import ibm_boto3
from ibm_botocore.client import Config, ClientError

# NVVpHf46mQjkZObILVTUGuivEZSZI-JXyAbwhYG4FxtX
credentials_path = "C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/flask_api/ibm-safety-net-f2a46-d8e10147131d.json"

def upload_to_gcs(file_obj, bucket_name, remote_path, credentials):

    client = storage.Client.from_service_account_json(credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(remote_path)
    # Делает объект доступным для всех
    blob.make_public()

    # Загружаем объект из файлового потока
    blob.upload_from_file(file_obj)



def detect_gesture(video_source):
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    model = load_model("C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/models/hand_gest/mp_hand_gesture")

    f = open("C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/models/hand_gest/gesture.names", "r")
    classNames = f.read().split("\n")
    f.close()
    cap = cv2.VideoCapture(video_source)
    gesture_count = 0
    video_count = 0
    curr_frame = 0
    frames = []
    frame_count = 0
    max_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or (max_frames > 0 and frame_count >= max_frames):
            print("Видео достигло конца.")
            break

        x, y, c = frame.shape

        frame = cv2.flip(frame, 1)
        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands.process(framergb)

        className = ""

        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    lmx = int(lm.x * x)
                    lmy = int(lm.y * y)

                    landmarks.append([lmx, lmy])

                mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

            prediction = model.predict([landmarks])
            classID = np.argmax(prediction)
            className = classNames[classID]
            if className == "call me":
                gesture_count += 1
            else:
                gesture_count = 0
            if gesture_count == 60:
                print("Danger detected")
                for i in range(101, 1, -1):
                    frames.append(cv2.imread("C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/images/" + str(curr_frame - i) + ".jpg"))
                frame_height, frame_width, _ = frames[0].shape
                output_filename = f"C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/alert_danger/alert_{video_count}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"avc1")
                fps = 30
                out = cv2.VideoWriter(
                    output_filename, fourcc, fps, (frame_width, frame_height)
                )
                for frame in frames:
                    out.write(frame)
                out.release()

                with open(f"C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/alert_danger/alert_{video_count}.mp4", "rb") as f:
                    upload_to_gcs(f, "industrial-safety", f"fire_alert_{video_count}.mp4",  credentials_path)
                final_data = {
                    "camera_id": "45fgQn7oYaLFaG8SFesT",
                    "video_link": f"https://ibmhacktesting1-donotdelete-pr-stnyxpwdejeura.s3.jp-tok.cloud-object-storage.appdomain.cloud/danger_alert_{video_count}.mp4",
                    "timestamp": {
                        "year": datetime.now().year,
                        "month": datetime.now().month,
                        "day": datetime.now().day,
                        "hour": datetime.now().hour,
                        "minute": datetime.now().minute,
                        "second": datetime.now().second,
                    },
                }
                r = requests.post(
                    "https://4f74-188-163-102-99.ngrok-free.app/handgesture",
                    json=final_data,
                )
                video_count += 1
                frames = []
                exit()
        curr_frame += 1

    cap.release()
