# 사진 다운로드 되면 메타정보 추출하는 프로그램
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from PIL.ExifTags import TAGS
import requests


try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ModuleNotFoundError as e:
    print(e)
    os.system("pip install watchdog")

class Handler(FileSystemEventHandler):
    def on_created(self, event): # 파일 생성시
        print(f'event type : {event.event_type}\n'
              f'event src_path : {event.src_path}')
        if event.is_directory:
            print("디렉토리 생성")
        else: # not event.is_directory
            """
            Fname : 파일 이름
            Extension : 파일 확장자 
            """
            Fname, Extension = os.path.splitext(os.path.basename(event.src_path))
            '''
             1. jpg 파일
             2. zip 파일
             3. exe 파일
             4. lnk 파일
            '''
            if Extension == '.jpg' or Extension == '.JPG':
                print(event.src_path)
                process_image(event.src_path)

                

    def on_deleted(self, event):
        print(os.path.basename(event.src_path), '파일삭제')

    def on_moved(self, event): # 파일 이동시
        print(f'event type : {event.event_type}\n')

class Watcher:
    def __init__(self, path):
        print("[ Watching ]")
        self.event_handler = None      # Handler
        self.observer = Observer()     # Observer 객체 생성
        self.target_directory = path   # 감시대상 경로
        self.currentDirectorySetting() # instance method 호출 func(1)

    def currentDirectorySetting(self): # func (1) 현재 작업 디렉토리
        print("====================================")
        print("Directory :  ", end=" ")
        os.chdir(self.target_directory)
        print("{cwd}".format(cwd=os.getcwd()))
        print("====================================")

    def run(self): # func (2)
        self.event_handler = Handler() # 이벤트 핸들러 객체 생성
        self.observer.schedule(
            self.event_handler,
            self.target_directory,
            recursive=False
        )

        self.observer.start() 
        try:
            while True: 
                time.sleep(1) 
        except KeyboardInterrupt as e:
            print("[ Finish ]")
            self.observer.stop()


def lat_lon_to_addr(lon, lat):
    url = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={longitude}&y={latitude}'.format(longitude=lon, latitude=lat)
    api_key = "20e841d134e90cd157222ba545984e63"
    headers = {"Authorization": "KakaoAK " + api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        match_first = result['documents'][0]['address_name']
        return match_first
    else:
        return "Something went wrong!"



def process_image(image_path):
    
    season = {
        '01': '겨울',
        '02': '겨울',
        '03': '봄',
        '04': '봄',
        '05': '여름',
        '06': '여름',
        '07': '여름',
        '08': '여름',
        '09': '가을',
        '10': '가을',
        '11': '겨울',
        '12': '겨울'
    }

    image = Image.open(image_path)
    info = image._getexif()  # 이미지 메타정보
    print(info)
    make_time = info.get(36867)  # 이미지 촬영 시간 정보 추출
    month = make_time[5:7] if make_time else None
    image_weather = season.get(month, "정보 없음")

    # GPSInfo 정보 추출(위도, 경도)
    gps_lat = None
    gps_lon = None

    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == 'GPSInfo':
            gps_lat = value.get(2) if 2 in value else None  # 위도
            gps_lon = value.get(4) if 4 in value else None  # 경도
            break

    if gps_lat and gps_lon:
        lat = (((gps_lat[2] / 60.0) + gps_lat[1]) / 60.0) + gps_lat[0]
        lon = (((gps_lon[2] / 60.0) + gps_lon[1]) / 60.0) + gps_lon[0]
        address = lat_lon_to_addr(lon, lat)
    else:
        lat = lon = None
        address = "정보 없음"

    print("파일명:", os.path.basename(image_path))
    print("날 씨:", image_weather)
    print("날 짜:", make_time if make_time else "정보 없음")
    print("위도 경도:", type((lat, lon)) if (lat and lon) else "정보 없음")
    print("주 소:", address)
    print("\n")

if __name__ == "__main__":
    myWatcher = Watcher(".")    # 사진이 들어가는 저장소 감시
    myWatcher.run()