# Window

import wmi

def set_brightness(brightness_level):
    wmi_instance = wmi.WMI(namespace="wmi")
    brightness = brightness_level / 100.0
    for monitor in wmi_instance.WmiMonitorBrightnessMethods():
        monitor.WmiSetBrightness(int(brightness * 100), 0)

def lock_screen():
    import ctypes
    ctypes.windll.user32.LockWorkStation()

def main():
    while True:
        try:
            brightness = int(input("밝기를 입력하세요 (10-100), 화면을 잠그려면 0을 입력하세요: "))
            if brightness == 0:
                lock_screen()
                print("화면이 잠겼습니다.")
            elif 10 <= brightness <= 100:
                set_brightness(brightness)
                print(f"밝기가 {brightness}로 설정되었습니다.")
            else:
                print("잘못된 입력입니다. 10부터 100 사이의 숫자를 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")

if __name__ == "__main__":
    main()


# Jetson nano (ubuntu)

import Jetson.GPIO as GPIO
import socket
import subprocess
import time


SERVO_PIN = 33

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(7.5)  # 중앙값(0도)에 해당하는 듀티 사이클 시작

def move_servo(angle):
    if -180 <= angle <= 180:
        # -180도는 듀티 사이클 2.5, 0도는 7.5, 180도는 12.5로 설정
        DC = (angle + 180) * (10.0 / 360.0) + 2.5
        pwm.ChangeDutyCycle(DC)


HOST = '0.0.0.0'  # 모든 IP 주소에 대해 수신 대기
PORT = 12345  # 포트 번호

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


def set_display_brightness(brightness):
    try:
        # xrandr 명령을 사용하여 디스플레이 밝기 설정
        if brightness == 0.1:
            # 0.1인 경우 3초 뒤에 작동하도록 설정
            time.sleep(3)
        subprocess.run(['xrandr', '--output', 'HDMI-0', '--brightness', str(brightness)])
        print("디스플레이 밝기가 설정되었습니다.")
    except Exception as e:
        print("디스플레이 밝기 설정 중 오류 발생:", e)



power_saving_mode = False

while True:
    # 클라이언트로부터 메시지 수신
    data = client_socket.recv(1024)
    if not data:
        break
    
    # 수신한 메시지 출력
    message = data.decode('utf-8')
    if message == "절전":
        set_display_brightness(0.1)
        power_saving_mode = True
        continue
    else:
        if power_saving_mode:
            set_display_brightness(0.9)
            distance = float(message)
        else:
            distance = float(message)
    # print("거리:", distance)
    
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
