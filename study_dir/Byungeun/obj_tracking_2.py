import Jetson.GPIO as GPIO
import time
from ultralytics import YOLO
import numpy as np
import cv2

# PWM 핀 설정 (Jetson Nano의 핀 번호에 따라 조정 필요)
servo_pin = 33
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servo_pin, GPIO.OUT)

# PWM 주파수 설정 (MG996R의 경우 일반적으로 50Hz)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

def set_servo_angle(angle):
    duty_cycle = (angle / 18.0) + 2.5
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# YOLO 모델 로드
model = YOLO("yolov8n.pt")

# 비디오 캡쳐 객체 초기화
cap = cv2.VideoCapture(0)

# 화면 중앙 값 계산
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_center = frame_width // 2

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 프레임을 YOLO 모델에 입력
        results = model.predict(frame, classes=[0])  # 클래스 0은 'person'
        
        # 검출된 객체 중 가장 큰 객체 사용
        detections = results.pandas().xyxy[0]  # 결과를 Pandas DataFrame으로 변환
        if not detections.empty:
            largest_object = detections.loc[detections['area'].idxmax()]
            x_center = (largest_object['xmin'] + largest_object['xmax']) / 2
            error = frame_center - x_center
            
            if abs(error) > frame_width * 0.1:  
                # Calculate desired angle change based on error magnitude
                angle_change = (error / frame_width) * 90  # Scale error to servo angle change
                current_angle = 90 + angle_change  # Assuming 90 is center position
                set_servo_angle(current_angle)
        
        cv2.imshow('YOLO v8 Detection', np.squeeze(results.render()))
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    pwm.stop()
    GPIO.cleanup()
    cap.release()
    cv2.destroyAllWindows()
