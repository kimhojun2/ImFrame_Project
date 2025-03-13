import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# 모터 제어에 필요한 라이브러리 또는 모듈 import
import RPi.GPIO as GPIO
import time

# GPIO 핀 번호 설정
motor_pin = 33

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)

# PWM 객체 생성
pwm = GPIO.PWM(motor_pin, 50) # 주파수 50Hz 설정

gst_pipeline = (
    'nvarguscamerasrc sensor-id=0 ! '
    'video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=30/1 ! '
    'nvvidconv flip-method=0 ! '
    'video/x-raw, width=1920, height=1080, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'
)

# 영상 프레임을 처리하는 함수
def process_frames(cap, face_detection):
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("웹캠을 찾을 수 없습니다.")
            break

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_detection.process(image)

        # 얼굴 감지 결과의 개수를 세기
        num_detections = 0
        max_box_size = 0
        max_box_center_x = 0
        if results.detections:
            num_detections = len(results.detections)
            for detection in results.detections:
                box = tuple(detection.location_data.relative_bounding_box)
                box_size = box.width * box.height
                if box_size > max_box_size:
                    max_box_size = box_size
                    max_box_center_x = box.x + box.width / 2

        # 터미널에 얼굴 인식 개수와 가장 큰 객체의 중앙값 출력
        print("인식된 얼굴 개수:", num_detections)
        print("가장 큰 객체의 중앙값:", max_box_center_x)

        # 모터 제어 코드 추가
        move_motor_to_center(max_box_center_x)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(image, detection)
        # cv2.imshow('MediaPipe Face Detection', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

# 모터를 움직이는 함수
def move_motor_to_center(center_x):
    # 중앙에서의 오차를 계산
    center_error = 0.5 - center_x

    # 모터를 회전시키는 코드 작성
    # 여기에서는 간단한 예시로 PWM을 사용하여 모터를 회전시키는 코드를 작성했습니다.
    # 필요에 따라 실제 하드웨어에 맞게 모터 제어 코드를 수정해야 합니다.
    duty_cycle = 7.5 + center_error * 2
    pwm.start(duty_cycle)
    time.sleep(0.1)
    pwm.stop()

# 가중치 파일 경로
cascade_filename = 'haarcascade_frontalface_alt.xml'
# 모델 불러오기
cascade = cv2.CascadeClassifier(cascade_filename)

# 웹캠으로부터 영상을 읽어오기 위해 OpenCV VideoCapture 객체 생성
cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
# 얼굴 감지 모델 초기화
with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    # 프레임 처리 함수 호출
    process_frames(cap, face_detection)

# 웹캠 리소스 해제
cap.release()
# OpenCV 윈도우 종료
cv2.destroyAllWindows()
