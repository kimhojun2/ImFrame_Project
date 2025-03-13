from ultralytics import YOLO
import numpy


model = YOLO("yolov8n.pt")

result = model.predict(source=0, stream=True, show=True, tracker="bytetrack.yaml", classes=0)