from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QEvent, QObject, QTimer
from PyQt5.QtGui import QPixmap
import sys
import os
# from .touch_image import TouchImage
# from .mic_image import MicImage
# from .motion_sensor_image import MotionSensorImage
# from .image_load import ImageLoaderThread
import requests
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO
import threading
from cam import camera
# from cam_test_2_lbe import tracking
from queue import Queue
import time
import pvporcupine
import numpy as np
import struct
import subprocess
import requests
from pvrecorder import PvRecorder
import sounddevice as sd
import cv2
# import jetson_inference
# import jetson_utils
# import Jetson.GPIO as GPIO
import vlc
import serial



module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sharing'))
if module_path not in sys.path:
    sys.path.append(module_path)

from firebase_admin_setup import initialize_firebase, get_firestore_client
import sqlite_utils

api_key = "20e841d134e90cd157222ba545984e63"

arduino = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    timeout=5,
    xonxoff=False,
    rtscts=True, 
    dsrdtr=False,
    write_timeout=2
)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)


# delay 선택해서 스마트싱스 루틴 실행
def send_zigbee(delay):
    GPIO.output(7, GPIO.LOW)                                                                           

    print("지그비 신호 송신")
    time.sleep(delay)
    GPIO.output(7, GPIO.HIGH)

    print("지그비 신호 중단")

# display_image.py
#다운로드 이미지 저장
class ImageProcessor:
    season_list = {'01':'겨울',
        '02':'겨울',
        '03':'봄',
        '04':'봄',
        '05':'여름',
        '06':'여름',
        '07':'여름',
        '08':'여름',
        '09':'가을',
        '10':'가을',
        '11':'겨울',
        '12':'겨울'}
    
    def __init__(self, download_path, db_path):
        self.download_path = download_path
        self.db = sqlite_utils.Database(db_path)
        # self.index = 0
        last_record = list(self.db.query("SELECT max(id) as last_id FROM album"))
        self.index = (last_record[0]['last_id'] or 0) + 1 if last_record else 1

        self.vlc_instance = vlc.Instance('--aout=pulse')
        self.player = self.vlc_instance.media_player_new()
        self.voice_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'voice')
        self.share_voice = os.path.join(self.voice_dir, 'share.mp3')

    def play_sound(self, audio_file):
        """ Play a given audio file using VLC """
        if self.player.is_playing():
            self.player.stop()  # Stop any currently playing audio
        media = self.vlc_instance.media_new(audio_file)
        self.player.set_media(media)
        self.player.play()

    def download_image(self, image_url):
        album_folder = self.download_path
        if not os.path.exists(album_folder):
            os.makedirs(album_folder)
        
        file_name = f"{self.index}.jpg"
        local_path = os.path.join(album_folder, file_name)
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            print(f"이미지 다운로드 완료: {local_path}")
            self.index += 1
            return local_path
        else:
            print("이미지를 다운로드하는 데 문제가 발생했습니다.")
            return None

    def image_info_to_db(self, image_path):
        try:
            image = Image.open(image_path)
            ###########

            # Hardcoded network
            network = 'ssd-mobilenet-v2'

            # Hardcoded overlay
            overlay = 'box,labels,conf'

            # Hardcoded detection threshold
            threshold = 0.5

            # Hardcoded labels file path
            labels_file = '/home/jetson/Desktop/hjw/detect/labels.txt'

            # Load the object detection network
            net = jetson_inference.detectNet(network, threshold)

            # Load class labels
            class_labels = []
            with open(labels_file, 'r') as f:
                class_labels = [line.strip() for line in f.readlines()]

            # Load the image
            img = cv2.imread(image_path)

            if img is not None:
                # Convert the image to RGBA (required for jetson-inference)
                img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

                # Allocate CUDA memory for the image
                cuda_img = jetson_utils.cudaFromNumpy(img_rgba)

                # Detect objects in the image (with overlay)
                detections = net.Detect(cuda_img, img.shape[1], img.shape[0], overlay=overlay)

                # Print the detections
                tags = ''
                print("Detected objects in {}:".format(image_path))
                for detection in detections:
                    class_label = class_labels[detection.ClassID]
                    print("Class:", class_label)
                    if tags == '':
                        tags += class_label
                    else:
                        tags += f', {class_label}'
                    

            info = image._getexif()
            if info:
                metadata = {TAGS.get(tag, tag): value for tag, value in info.items()}
                make_time = metadata.get('DateTimeOriginal', "정보 없음")
                month = make_time[5:7] if make_time != "정보 없음" else None
                image_weather = self.season_list.get(month, "정보 없음")
                gps_info = metadata.get('GPSInfo')
                gps_lat = gps_lon = None
                if gps_info:
                    gps_lat = self.convert_to_decimal(gps_info.get(2)) if 2 in gps_info else None
                    gps_lon = self.convert_to_decimal(gps_info.get(4)) if 4 in gps_info else None
                address = self.lat_lon_to_addr(gps_lon, gps_lat) if gps_lat and gps_lon else "정보 없음"
                image_info = {
                    "title": os.path.basename(image_path),
                    "image": image_path,
                    "season": image_weather,
                    "date": make_time,
                    "gps": (gps_lat, gps_lon),
                    "address": address,
                    "tags": tags
                }
                self.db["album"].insert(image_info)
                print("데이터베이스에 정보 저장 완료")
                self.play_sound(self.share_voice)
        except Exception as e:
            print(f"메타데이터 추출 및 저장 중 오류 발생: {e}")

    def convert_to_decimal(self, gps_data):
        degrees, minutes, seconds = gps_data
        return degrees + (minutes / 60.0) + (seconds / 3600.0)

    def lat_lon_to_addr(self, lon, lat):
        url = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={longitude}&y={latitude}'.format(longitude=lon, latitude=lat)
        headers = {"Authorization": "KakaoAK " + api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result['documents'][0]['address_name'] if result['documents'] else "No Address Found"
        else:
            return "No Data"

#firebase 별도 스레드 생성
class ImageUpdateEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, image_url):
        super().__init__(ImageUpdateEvent.EVENT_TYPE)
        self.image_url = image_url

class FirebaseThread(threading.Thread):
    def __init__(self, uid, callback):
        super().__init__()
        self.uid = uid
        self.callback = callback
        
        
        
    def setup_gpio(self):
        self.led_pin = 15
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led_pin, GPIO.OUT)
        
        
        # 오디오 파일 재생 시작까지 대기
        while self.player.get_state() != vlc.State.Playing:
            time.sleep(0.1)
        # 오디오 파일 재생 완료까지 대기
        while self.player.get_state() == vlc.State.Playing:
            time.sleep(0.1)

    def run(self):
        db = get_firestore_client()
        user_doc = db.collection('users').document(self.uid)
        if user_doc.get().exists:
            groups = user_doc.get().to_dict().get('groups', [])
            for group_name in groups:
                self.monitor_group_images(group_name)

    def monitor_group_images(self, group_name):
        db = get_firestore_client()
        group_doc = db.collection('group').document(group_name)
        group_doc.on_snapshot(self.handle_snapshot)

    def handle_snapshot(self, doc_snapshot, changes, read_time):
        print("Snapshot received")
        for doc in doc_snapshot:
            img_url = doc.to_dict().get('img_url', None)
            if img_url:
                QtCore.QCoreApplication.postEvent(self.callback, ImageUpdateEvent(img_url))
                
                
# 디스플레이 조작 관련
class DisplayImage(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(DisplayImage, self).__init__(parent)
        self.images = []
        self.current_image_index = 0
        self.setupUi()
        self.installEventFilter(self)
        self.processor = ImageProcessor(os.path.abspath(os.path.join(os.path.dirname(__file__), 'album')), "local.db")
        self.image_update_timer = QTimer(self)  # 이미지 업데이트를 위한 타이머
        self.image_update_timer.timeout.connect(self.load_images)  # load_images 함수 연결
        self.image_update_timer.start(3000) #3초마다 리스트 재탐색
        from STT import SpeechToText
        self.stt_instance = SpeechToText(self)
        self.stt_instance.image_signal.connect(self.display_image)
        
    def eventFilter(self, source, event):
        if event.type() == ImageUpdateEvent.EVENT_TYPE:
            self.update_image_from_url(event.image_url)
            return True
        return super().eventFilter(source, event)

    def setupUi(self):
        self.current_image_index = 0  # 현재 이미지 인덱스 초기화
        self.index = 0  # 다운로드 인덱스 초기화
        self.is_group_image_displayed = False
        self.showFullScreen()
        self.setScaledContents(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.load_images()
        self.initialize_firebase()

    def load_images(self):
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Display', 'album'))
        new_images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        new_image_set = set(new_images)
        
        if new_image_set != set(self.images):
            added_images = list(new_image_set - set(self.images))
            removed_images = list(set(self.images) - new_image_set)
            
            # 현재 이미지 리스트 업데이트
            self.images = new_images
            print("이미지 목록 업데이트됨")

            # 현재 보고 있는 이미지의 인덱스 계산
            if self.images and self.current_image_index < len(self.images):
                # 이미지 인덱스가 범위 안에 있는 경우, 같은 이미지 유지
                current_image = self.images[self.current_image_index]
                if current_image in removed_images:
                    # 현재 보고 있는 이미지가 제거된 경우, 첫 번째 이미지 표시
                    self.current_image_index = 0
                    self.display_image(self.images[0])
                else:
                    # 현재 이미지 유지
                    self.current_image_index = self.images.index(current_image)
            elif self.images:
                # 이미지가 있지만 인덱스가 범위를 벗어나면 처음부터 시작
                self.current_image_index = 0
                self.display_image(self.images[0])
            else:
                # 이미지가 없는 경우
                self.setText("이미지가 없습니다.")
            
    def display_image(self, image_path):
        pixmap = QtGui.QPixmap(image_path)
        if not pixmap.isNull():
            transform = QtGui.QTransform().rotate(90)
            rotated_pixmap = pixmap.transformed(transform, QtCore.Qt.SmoothTransformation)
            self.setPixmap(rotated_pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            print(f"이미지 표시 성공: {image_path}")
        else:
            print(f"이미지 로드 실패: {image_path}")
            self.setText("이미지를 로드할 수 없습니다.")
            
    def safe_display_image(self, image_path):
        QtCore.QMetaObject.invokeMethod(self, "display_image", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, image_path))
        
    def update_image_from_url(self, image_url):
        local_path = self.processor.download_image(image_url)
        if local_path:
            self.display_image(local_path)
            self.processor.image_info_to_db(local_path)

    def initialize_firebase(self):
        initialize_firebase()
        self.uid = self.read_uid_file()
        if self.uid:
            self.start_firebase_thread()

    def start_firebase_thread(self):
        self.firebase_thread = FirebaseThread(self.uid, self)
        self.firebase_thread.start()

    def read_uid_file(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sharing', 'uid.txt')
        try:
            with open(path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("UID file not found.")
            return None
        
    def mousePressEvent(self, event):
        QtWidgets.QApplication.instance().quit()
    # if self.is_group_image_displayed:
    #     self.display_image(self.images[self.current_image_index])
    # else:
    #     super().mousePressEvent(event)

    #키보드로 사진 전환 및 종료
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            QtWidgets.QApplication.instance().quit()
        elif event.key() == QtCore.Qt.Key_Right:
            self.next_image()
        elif event.key() == QtCore.Qt.Key_Left:
            self.previous_image()
            self.ToF_gesture()

    #다음 이미지로 전환
    def next_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.display_image(self.images[self.current_image_index])
    #이전 이미지로 전환
    def previous_image(self):
        # if self.images:
        #     self.current_image_index = (self.current_image_index - 1) % len(self.images)
        #     self.display_image(self.images[self.current_image_index])

        self.ToF_gesture()

    # def ToF_gesture(self):
    #     start_time = time.time()  # 시작 시간 기록
    #     try:
    #         while True:
    #             # 현재 시간과 시작 시간의 차이가 10초를 넘으면 반복문 탈출
    #             if time.time() - start_time > 10:
    #                 print("Timeout: No gesture detected within 10 seconds.")
    #                 break

    #             if arduino.in_waiting > 0:  # 데이터가 버퍼에 존재하는지 확인
    #                 data = arduino.readline()  # 데이터 읽기
    #                 decoded_data = data.decode().strip()  # 데이터 디코딩 및 공백 제거

    #                 # "no detection"가 아니면 스마트싱스 로직 실행
    #                 if decoded_data != "no detection":
    #                     print(f"Gesture Detected: {decoded_data}")
    #                     self.execute_smartthings_logic(decoded_data)
    #                     break
    #                 else:
    #                     print("No gesture detected.")
    #             else:
    #                 time.sleep(0.01)  # 데이터가 없으면 잠시 대기

    #     except Exception as e:
    #         print(e)

    # def execute_smartthings_logic(self, gesture):
    #     if gesture == "smart":
    #         send_zigbee(0.3)
    #     elif gesture == "fist":
    #         send_zigbee(0.3)
    #     elif gesture == "circle":
    #         send_zigbee(0.3)


    def ToF_gesture(self):
        start_time = time.time()  # 시작 시간 기록
        gesture_detected = False 
        try:
            offset = 2
            while True:
                # 현재 시간과 시작 시간의 차이가 10초를 넘으면 반복문 탈출
                if time.time() - start_time > 10:
                    print("Timeout: No gesture detected within 10 seconds.")
                    break

                if arduino.in_waiting > 0:  # 데이터가 버퍼에 존재하는지 확인
                    data = arduino.readline()  # 데이터 읽기
                    decoded_data = data.decode().strip()  # 데이터 디코딩 및 공백 제거

                    if decoded_data == "no detection":
                        gesture_detected = False  # Reset flag if no detection
                        print("No gesture detected.")
                    elif not gesture_detected:
                        # If there was a detection and it's the first since a no detection
                        print(f"Gesture Detected: {decoded_data}")
                        self.execute_smartthings_logic(decoded_data, offset)
                        offset += 1
                        gesture_detected = True  # Set flag to True to avoid multiple triggers
                        break
                else:
                    time.sleep(0.01)  # 데이터가 없으면 잠시 대기

        except Exception as e:
            print(e)

    def execute_smartthings_logic(self, gesture, offset):
        if gesture == "smart":
            send_zigbee(2.2)
        elif gesture == "fist":
            send_zigbee(2.2)
        elif gesture == "circle":
            send_zigbee(2.2)



#음성 인식 관련
class Listen(QThread):
    def __init__(self, display):
        super().__init__()
        self.display = display
        self.lock = threading.Lock()
        # self.access_key = "BiQeBmnb2sGBb+/o+rlSbgRVOVR3YHdehy2oziBrO5QJLI2b09/Jgg==" #윈도우용
        self.access_key = "FhAnpcW7ncfjPsj3iGxCaLjFRLW1mhU8Z/N8m71XCIjJqw3s/akBUw==" #리눅스용
        self.current_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'wakeword')
        self.keyword_album = os.path.join(self.current_dir, '스마트뷰.ppn')
        self.keyword_next = os.path.join(self.current_dir, '다음사진.ppn')
        self.keyword_previous = os.path.join(self.current_dir, '이전사진.ppn')
        self.model_path = os.path.join(self.current_dir, 'porcupine_params_ko.pv')
        self.porcupine = None
        self.recorder = None
        self.init_porcupine_and_recorder()
        self.setup_gpio()
        
        self.vlc_instance = vlc.Instance('--aout=pulse')
        self.player = self.vlc_instance.media_player_new()
        self.voice_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'voice')
        self.start_voice = os.path.join(self.voice_dir, 'say.mp3')
        self.end_voice = os.path.join(self.voice_dir, 'exit.mp3')
        
    def setup_gpio(self):
        self.led_pin = 15
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led_pin, GPIO.OUT)
        
    def play_sound(self, audio_file):
        """ Play a given audio file using VLC """
        if self.player.is_playing():
            self.player.stop()  # Stop any currently playing audio
        media = self.vlc_instance.media_new(audio_file)
        self.player.set_media(media)
        self.player.play()
        
        # 오디오 파일 재생 시작까지 대기
        while self.player.get_state() != vlc.State.Playing:
            time.sleep(0.1)
        # 오디오 파일 재생 완료까지 대기
        while self.player.get_state() == vlc.State.Playing:
            time.sleep(0.1)
        
    def init_porcupine_and_recorder(self):
        with self.lock:
            try:
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keyword_paths=[self.keyword_album, self.keyword_next, self.keyword_previous],
                    model_path=self.model_path
                )
                self.recorder = PvRecorder(frame_length=self.porcupine.frame_length, device_index=0)
                self.recorder.start()
                print("Recorder and Porcupine initialized successfully.")
                GPIO.output(self.led_pin, GPIO.LOW)
                GPIO.output(self.led_pin, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.led_pin, GPIO.LOW)
                time.sleep(0.2)
                GPIO.output(self.led_pin, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.led_pin, GPIO.LOW)
                time.sleep(0.2)
                GPIO.output(self.led_pin, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.led_pin, GPIO.LOW)
                time.sleep(0.2)
                # GPIO.cleanup()
                # print("GPIO cleanup successful.")
            except Exception as e:
                print(f"Failed to initialize Porcupine or Recorder: {e}")
                QtCore.QTimer.singleShot(1000, self.init_porcupine_and_recorder)  # 재시도

    def run(self):
        print("Listening... Press Ctrl+C to exit")
        while True:
            try:
                if self.recorder is None or self.porcupine is None:
                    # print("Recorder or Porcupine not ready, waiting...")
                    time.sleep(1)
                    continue

                pcm_frame = self.recorder.read()
                keyword_index = self.porcupine.process(pcm_frame)
                if keyword_index >= 0:
                    self.wake_word_callback(keyword_index)
            except Exception as e:
                print(f'Error during processing: {e}')
            # finally:
            #     self.cleanup()
            #     self.init_porcupine_and_recorder()
    
    #종료로직
    def cleanup(self):
        with self.lock:  # Lock을 사용하여 동시 접근 제어
            try:
                if self.recorder:
                    self.recorder.stop()
                    self.recorder.delete()
                    self.recorder = None
                    print("Recorder stopped and deleted successfully.")
            except Exception as e:
                print(f"Failed to stop PvRecorder: {e}")

            try:
                if self.porcupine:
                    self.porcupine.delete()
                    self.porcupine = None
                    print("Porcupine instance deleted successfully.")
            except Exception as e:
                print(f"Failed to delete Porcupine instance: {e}")

    def wake_word_callback(self, keyword_index):
        if keyword_index == 0:
            print("Album keyword detected!")
            self.play_sound(self.start_voice)
            self.obj_tracking()
            self.cleanup()
            self.start_stt_process()
            # self.restart_recorder()
        elif keyword_index == 1:
            print("Next photo keyword detected!")
            self.display.next_image()
        elif keyword_index == 2:
            print("Previous photo keyword detected!")
            self.display.previous_image()

    def obj_tracking(self):
        self.ssd_tracking = threading.Thread(target=cracker.User_Tracking)
        self.ssd_tracking.start()
        print("트래킹 스레드 시작")


    def start_stt_process(self):
        from STT import SpeechToText
        self.display.stt = SpeechToText(self.display)
        self.display.stt.restart_listener.connect(self.restart_recorder)
        self.display.stt_thread = threading.Thread(target=self.display.stt.run)
        self.display.stt_thread.start()
        
    def restart_recorder(self):
        print("Restarting Porcupine and recorder...")
        self.cleanup()  # 기존 리소스 정리
        time.sleep(1)
        QtCore.QTimer.singleShot(1000, self.init_porcupine_and_recorder)


class CheckMessage:
    def __init__(self, swipe_queue, display):
        self.swipe_queue = swipe_queue
        self.display_ins = display
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(7, GPIO.OUT)

    def check_messages(self):
        while True:
            if not self.swipe_queue.empty():
                message = self.swipe_queue.get()
                if message == 'next':
                    print(message)
                    display.next_image()
                elif message == 'back':
                    print(message)
                    display.previous_image()
                elif message == 'scene_play':
                    send_zigbee(1)

                #     # 스마트싱스 정보
                #     scene_id = 'ec22f091-90b4-4f91-8e23-a2783326bad3'  # 스마트싱스 scene ID
                #     oauth_token = '8cd2da5e-e34e-4fe5-b38d-7b48301f03fb'  # OAuth 토큰
                #     url = f'https://api.smartthings.com/scenes/{scene_id}/execute'  # API 엔드포인트

                #     # HTTP 헤더 설정
                #     headers = {
                #         'Authorization': f'Bearer {oauth_token}',
                #         'Content-Type': 'application/json'
                #     }

                #     # API 요청
                #     response = requests.post(url, headers=headers)

                #     # 응답 확인
                #     if response.status_code == 200:
                #         print("스마트싱스 자동화 실행")
                #         print(response.json())  # 성공 시 응답 내용 출력
                #     else:
                #         print("스마트싱스 실패:", response.status_code, response.text)  # 실패 시 오류 메시지 출력


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    display = DisplayImage()
    listen_thread = Listen(display)
    listen_thread.start()
    db = sqlite_utils.Database("local.db")
    # db["album"].create({
    # "id": int,
    # "title": str,
    # "image": str,
    # "season": str,
    # "date": str,
    # "gps": tuple,
    # "address": str,
    # "tags": str
    # }, pk="id")
    cracker = tracking()
    # tracker = camera()
    # tracking_thread = threading.Thread(target=tracker.detect_objects_and_poses)
    # tracking_thread.start()
    # swipe_queue = tracker.get_swipe_queue()
    # check_message_thread = threading.Thread(target=CheckMessage(swipe_queue, display).check_messages)
    # check_message_thread.start()
    sys.exit(app.exec_())



    # touch_manager = TouchImage(display.label)
    # display.label.installEventFilter(touch_manager)
    # display.show()
