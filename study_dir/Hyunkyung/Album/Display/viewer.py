from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QEvent, QObject
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

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sharing'))
if module_path not in sys.path:
    sys.path.append(module_path)

from firebase_admin_setup import initialize_firebase, get_firestore_client
import sqlite_utils

api_key = "20e841d134e90cd157222ba545984e63"


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
        self.index = 0

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
                    "address": address
                }
                self.db["album"].insert(image_info)
                print("데이터베이스에 정보 저장 완료")
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
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.installEventFilter(self)
        self.processor = ImageProcessor(os.path.abspath(os.path.join(os.path.dirname(__file__), 'album')), "local.db")
        
    def eventFilter(self, source, event):
        if event.type() == ImageUpdateEvent.EVENT_TYPE:
            self.update_image_from_url(event.image_url)
            return True
        return super().eventFilter(source, event)

    def setupUi(self):
        self.showFullScreen()
        self.setScaledContents(True)
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)
        self.load_images()
        self.initialize_firebase()
        self.current_image_index = 0  # 현재 이미지 인덱스 초기화
        self.index = 0  # 다운로드 인덱스 초기화
        self.is_group_image_displayed = False
        
    def load_images(self):
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Display', 'images'))
        self.images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if self.images:
            self.display_image(self.images[0])
            
    def display_image(self, image_path):
        try:
            print(f"로딩 시도: {image_path}")  # 로딩 시도 로그 출력
            if image_path.lower().endswith('.gif'):
                movie = QtGui.QMovie(image_path)
                self.setMovie(movie)
                movie.start()
            else:
                pixmap = QtGui.QPixmap(image_path)
                if pixmap.isNull():
                    raise Exception("Pixmap is null, 이미지 로드 실패")
                self.original_pixmap = pixmap
                self.setPixmap(pixmap)
        except Exception as e:
            print(f"이미지 로드 실패: {e}")  # 이미지 로드 실패 로그 출력
            self.setText(f"이미지 로드 실패: {e}")  # 화면에 실패 메시지 출력
            
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
            
    #모션센서용 줌인줌아웃 테스트
    # def wheelEvent(self, event):
    #     if event.angleDelta().y() > 0:
    #         self.motion_sensor.on_motion_zoom_in(event.pos())
    #     else:
    #         self.motion_sensor.on_motion_zoom_out(event.pos())
    # def mouseReleaseEvent(self, event):
    #     self.motion_sensor.stop_zoom()

    #터치로 사진 전환
    # def mousePressEvent(self, event):
    #     if event.x() > self.width() / 2:
    #         self.next_image()
    #     else:
    #         self.previous_image()
    
    #키보드로 사진 전환 및 종료
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            QtWidgets.QApplication.instance().quit()
        elif event.key() == QtCore.Qt.Key_Right:
            self.next_image()
        elif event.key() == QtCore.Qt.Key_Left:
            self.previous_image()

    #다음 이미지로 전환
    def next_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.display_image(self.images[self.current_image_index])
    #이전 이미지로 전환
    def previous_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.display_image(self.images[self.current_image_index])



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    display = DisplayImage()
    db = sqlite_utils.Database("local.db")
    # db["album"].create({
    # "id": int,
    # "title": str,
    # "image": str,
    # "season": str,
    # "date": str,
    # "gps": tuple,
    # "address": str
    # }, pk="id")
    # touch_manager = TouchImage(display.label)
    # display.label.installEventFilter(touch_manager)
    # display.show()
    sys.exit(app.exec_())
