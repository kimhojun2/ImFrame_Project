
import jetson.inference
import jetson.utils
import Jetson.GPIO as GPIO


def __init__(self, servo_pin=33):
        # 서보 모터 핀 및 초기화
        SERVO_PIN = servo_pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(SERVO_PIN, 50)
        self.pwm.start((1./18.)*100 + 2)  # 중앙값(0도)에 해당하는 듀티 사이클 시작
        # 네트워크 초기화
        self.net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.3)
        self.cam = jetson.utils.videoSource("csi://0")


def User_Tracking(self):


    # 캡쳐 및 객체 인식 실행
    img = self.cam.Capture()
    detections = self.net.Detect(img)

    # 가장 큰 객체 찾기
    largest_area = 0
    largest_center_x = img.width / 2
    for detection in detections:
        print(detection.ClassID)
        if detection.ClassID == 0:  # person 클래스 ID 사용
            area = detection.Width * detection.Height
            if area > largest_area:
                largest_area = area
                largest_center_x = detection.Center[0]

    # 인식 결과를 이미지에 박싱
    for detection in detections:
        print(f"Detected object: {self.net.GetClassDesc(detection.ClassID)} with confidence {detection.Confidence}")
        jetson.utils.cudaDrawRect(img, detection.ROI, (255, 0, 0, 150))  # 빨간색 박스

    # 이미지 파일로 저장
    jetson.utils.saveImageRGBA("detected_frame.jpg", img, img.width, img.height)


    if len(detections) == 0:
        print("겍체 X")

    # 화면 중앙과의 거리 계산
    screen_center_x = img.width / 2
    distance_from_center = largest_center_x - screen_center_x

    # 상태 메시지 출력 및 모터 제어
    print(f"Distance from Center: {distance_from_center}")
    self.move_servo(distance_from_center, img.width)


if __name__ == "__main__":
    print('네임이 될까?')
    User_Tracking()