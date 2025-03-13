# git 제출용(Jetson Nano_khjtest.py)

import smbus2 as smbus
import threading
import time
import RPi.GPIO as GPIO  # Jetson Nano용 GPIO 라이브러리
import socket
import subprocess
import cv2

def capture_camera_and_save():
    # GStreamer 파이프라인 문자열 정의
    gst_pipeline = (
        'nvarguscamerasrc sensor-id=0 ! '
        'video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=30/1 ! '
        'nvvidconv flip-method=0 ! '
        'video/x-raw, width=1920, height=1080, format=(string)BGRx ! '
        'videoconvert ! '
        'video/x-raw, format=(string)BGR ! appsink'
    )

    # OpenCV에서 GStreamer 파이프라인 사용하여 카메라 열기
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다. 종료합니다.")
            break

        cv2.imshow('Camera Feed', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            cv2.imwrite('capture.png', frame)
            print("이미지가 저장되었습니다.")
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 함수 호출


I2C_CH = 0
BH1750_DEV_ADDR = 0x23

CONT_H_RES_MODE = 0x10

SERVO_PIN = 33

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(7.5)  # 중앙값(0도)에 해당하는 듀티 사이클 시작

HOST = '0.0.0.0'  # 모든 IP 주소에 대해 수신 대기
PORT = 12345  # 포트 번호

def readIlluminance():
    i2c = smbus.SMBus(I2C_CH)
    luxBytes = i2c.read_i2c_block_data(BH1750_DEV_ADDR, CONT_H_RES_MODE, 2)
    lux = int.from_bytes(luxBytes, byteorder='big')
    i2c.close()
    return lux

# def readIlluminanceThread():
#     while True:
#         print(f'{readIlluminance()} lux')
#         time.sleep(1)

def move_servo(angle):
    if -180 <= angle <= 180:
        # -180도는 듀티 사이클 2.5, 0도는 7.5, 180도는 12.5로 설정
        DC = (angle + 180) * (10.0 / 360.0) + 2.5
        pwm.ChangeDutyCycle(DC)

def set_display_brightness(brightness):
    try:
        subprocess.run(['xrandr', '--output', 'HDMI-0', '--brightness', str(brightness)])
        print(f"디스플레이 밝기가 {brightness}로 설정되었습니다.")
    except Exception as e:
        print("디스플레이 밝기 설정 중 오류 발생:", e)

def readIlluminanceAndAdjustBrightness():
    while True:
        lux = readIlluminance()
        print(f'{lux} lux')
        
        if lux < 100:
            set_display_brightness(0.1)  # 어두운 환경
        elif lux < 600:
            set_display_brightness(0.5)  # 중간 밝기
        else:
            set_display_brightness(1.0)  # 밝은 환경

        time.sleep(1)  # 1초 간격으로 반복

def server_thread():
    # 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)  # 백로그 큐의 크기 설정

    print("서버가 시작되었습니다.")

    # 클라이언트의 연결 수락
    client_socket, addr = server_socket.accept()
    print(addr)

    # 클라이언트가 연결되면 서보 모터를 90도로 설정
    move_servo(90)

    while True:
        # 클라이언트로부터 메시지 수신
        data = client_socket.recv(1024)
        if not data:
            break

        # 수신한 메시지 출력
        message = data.decode('utf-8')
        before_message = message
        print(message)
        # if message == "절전":
        #     # if before_message == '절전':
        #     #     continue
        #     set_display_brightness(0.1)
        #     continue
        # else:
        #     distance = float(message)
        #     set_display_brightness(1.0)
        distance = float(message)
        # 거리 값을 이용하여 서보 모터를 제어
        angle = 90 + (distance // 2)  # 예시: 거리에 따라 각도 조절
        if 0 <= angle <= 180:
            move_servo(angle)
            client_socket.sendall("OK".encode())

        else:
            # "OK" 응답 전송
            client_socket.sendall("OK".encode())

    # 연결 종료
    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    
    # 쓰레드 생성
    thread_camera = threading.Thread(target=capture_camera_and_save)
    thread_motr_control = threading.Thread(target=server_thread)
    thread_brightness_control = threading.Thread(target=readIlluminanceAndAdjustBrightness)

    # 쓰레드를 데몬으로 설정
    thread_motr_control.daemon = True
    thread_brightness_control.daemon = True
    thread_camera.daemon = True

    # 쓰레드 시작
    thread_motr_control.start()
    thread_brightness_control.start()
    thread_camera.start()

    # 키 입력 대기, 엔터 키가 입력이 되면 다음으로 넘어가서 'done'을 출력하고 프로그램 종료
    input("Press Enter to exit\n")
    print('done')
