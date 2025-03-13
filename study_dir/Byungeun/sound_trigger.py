import pyaudio
import numpy as np
import time
import threading
import jetson.inference
import jetson.utils
import Jetson.GPIO as GPIO

# 서보 모터 설정
SERVO_PIN = 33
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(7.5)  # 중앙값(0도)에 해당하는 듀티 사이클 시작

# 객체 추적 및 인식 초기화
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("csi://0")

# 추적 상태 및 타이머
last_detection_time = None
detection_active = False
detection_timeout = 30  # 30초 동안 인식이 없으면 추적 종료

def object_detection():
    global last_detection_time, detection_active
    while detection_active:
        img = camera.Capture()
        detections = net.Detect(img)
        
        if len(detections) == 0:
            if time.time() - last_detection_time > detection_timeout:
                print("1")
                detection_active = False
                break
        else:
            last_detection_time = time.time()  # 인식 갱신

def start_detection():
    global last_detection_time, detection_active
    if not detection_active:
        detection_active = True
        last_detection_time = time.time()
        detection_thread = threading.Thread(target=object_detection)
        detection_thread.start()
        print(2)

# 오디오 스트림 콜백 함수
def audio_callback(in_data, frame_count, time_info, status):
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    volume = np.linalg.norm(audio_data) * 10
    print(volume)

    if volume > 1000:  # 볼륨 임계값 설정
        start_detection()
    return (in_data, pyaudio.paContinue)

# PyAudio 초기화
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                stream_callback=audio_callback)

# 스트림 시작
stream.start_stream()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    # 스트림 중지 및 종료
    stream.stop_stream()
    stream.close()
    p.terminate()
    detection_active = False  # 탐지 종료
