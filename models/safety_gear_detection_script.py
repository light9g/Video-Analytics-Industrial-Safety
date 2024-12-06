from PIL import Image
import torch
import math
from ultralytics import YOLO
import cv2
import requests
import time
import json
from datetime import datetime
import os

# Загрузка модели YOLO
# model = YOLO("C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/models/yolo_models/yolov8l.pt")
model = YOLO("C:/Users/Roman/PycharmProjects/Video Analytics Industrial Safety/models/yolo_models/best.pt")

def safety_gear(video_source):
    # Открытие видео
    cap = cv2.VideoCapture(video_source)

    # Проверка успешности открытия видео
    if not cap.isOpened():
        print("Ошибка: Видео не может быть открыто.")
        return

    # Получение параметров видео
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    output_directory = "processed_videos"
    output_filename = os.path.join(output_directory, "processed_safety_video.mp4")

    # Создание директории для сохранения видео
    os.makedirs(output_directory, exist_ok=True)

    # Инициализация объекта записи видео
    out = cv2.VideoWriter(
        output_filename,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (frame_width, frame_height)
    )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Выполнение анализа кадра с помощью YOLO
        results = model.predict(frame)
        counts = {}

        # Обработка результатов YOLO
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                # Координаты и класс объекта
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                confidence = box.conf[0]  # Уверенность
                class_name = model.names[cls]

                # Рисование прямоугольника и подписи
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{class_name} {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

                # Подсчет объектов
                if cls not in counts:
                    counts[cls] = 1
                else:
                    counts[cls] += 1

        # Формирование JSON-данных для отправки
        final = {}
        for key in counts.keys():
            final[model.names[key]] = counts[key]
        for vals in model.names.values():
            if vals not in final.keys():
                final[vals] = 0
        body = {
            "camera-id": "45fgQn7oYaLFaG8SFesT",
            "data": final,
            "timestamp": {
                "year": datetime.now().year,
                "month": datetime.now().month,
                "day": datetime.now().day,
                "hour": datetime.now().hour,
                "minute": datetime.now().minute,
                "second": datetime.now().second,
            },
        }
        r = requests.post("https://4f74-188-163-102-99.ngrok-free.app/safetygear", json=body)

        # Запись обработанного кадра в видео
        out.write(frame)

        # Задержка для отправки данных
        time.sleep(1)

    # Освобождение ресурсов
    cap.release()
    out.release()
    print(f"Обработанное видео сохранено как: {output_filename}")
