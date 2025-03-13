#!/usr/bin/env python3
import jetson.inference
import jetson.utils
import Jetson.GPIO as GPIO
import sounddevice as sd
import numpy as np
import time

# 서보 모터 핀 및 초기화
SERVO_PIN = 33
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(7.5)  # 중앙값(0도)에 해당하는 듀티 사이클 시작

def move_servo(pixel_distance, screen_width):
    # Deadzone 설정 (예: 화면 너비의 5%로 설정)
    deadzone = screen_width * 0.1  # 화면 중앙에서 ±5% 이내의 변화는 무시

    if abs(pixel_distance) < deadzone:
        print("Within deadzone, no motor movement required.")
        return

    angle = (pixel_distance / screen_width) * 180
    angle = max(min(angle, 90), -90)  # 서보 모터의 각도 제한

    DC = (angle + 180) * (10.0 / 360.0) + 2.5
    pwm.ChangeDutyCycle(DC)
    print(f"Moving servo to angle: {angle} degrees based on distance: {pixel-distance}")

def audio_callback(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    print(f"Volume: {volume_norm}")
    if volume_norm > 20:  # 조정 가능한 볼륨 임계값
        capture_and_process()

def capture_and_process():
    img = camera.Capture()
    detections = net.Detect(img)

    largest_area = 0
    largest_center_x = 0
    for detection in detections:
        if detection.ClassID == 1:  # 가정: ClassID 1은 대상 객체
            area = detection.Width * detection.Height
            if area > largest_area:
                largest_area = area
                largest_center_x = detection.Center[0]

    screen_center_x = img.width / 2
    distance_from_center = largest_center_x - screen_center_x

    print(f"Distance from Center: {distance_from_center}")
    move_servo(distance_from_center, img.width)

# 네트워크 초기화
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("csi://0")

# 사운드 감지를 위한 스트림 설정
stream = sd.InputStream(callback=audio_callback)
with stream:
    sd.sleep(10*1000)  # 10초 동암 사운드 감지를 유지, 필요에 따라 조절 가능
