import firebase_admin
from firebase_admin import credentials, messaging
import requests
import os
from PIL import Image
from PIL.ExifTags import TAGS
import requests
import sqlite_utils

# Firebase 프로젝트 인증 정보 다운로드
# cred = credentials.Certificate("./a407-35709-firebase-adminsdk-yim7q-2bcfc015e7.json")
# firebase_admin.initialize_app(cred)


db = sqlite_utils.Database("local.db")

# FCM 토픽 설정
# topic = "image_upload"


def download_save_image(image_url, local_path, file_name):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            print(f"이미지 다운로드 완료: {local_path}")
            image = Image.open(local_path)
            info = image._getexif()
            season, date, gps, address = image_info_to_db(info)
            image_info = {
                "title": file_name,
                "image": local_path,
                "season": season,
                "date": date,
                "gps": gps,
                "address": address
            }


            db["album"].insert(image_info)

        else:
            print("이미지를 다운로드하는 데 문제가 발생했습니다.")
    except Exception as e:
        print(f"이미지 다운로드 중 오류 발생: {e}")


def handle_message(message, index):
    '''
    if 'data' in message:
        data = message['data']
        if 'imageUrl' in data:
            image_url = data['imageUrl']
            # 로컬에 저장할 경로 및 파일명
            album_folder = "./album"
            if not os.path.exists(album_folder):
                os.makedirs(album_folder)
            file_name = f"{index}.jpg"
            local_path = os.path.join(album_folder, file_name)
            # 이미지 다운로드
            download_save_image(image_url, local_path, file_name)
    '''
    image_url = message
    album_folder = "./album"
    if not os.path.exists(album_folder):
        os.makedirs(album_folder)
    file_name = f"{index}.jpg"
    local_path = os.path.join(album_folder, file_name)
    # 이미지 다운로드
    download_save_image(image_url, local_path, file_name)
    
    

def listen_for_messages():
    index = 1
    # FCM 메시지 수신 대기
    '''
    response = messaging.subscribe_to_topic(topic)
    while True:
        messages = messaging.receive_message(response)
        for message in messages:
            handle_message(message)
            messaging.delete_message(response, message['message_id'])
    '''
    message = 'https://a407.s3.ap-northeast-2.amazonaws.com/trip.jpg'
    while True:
        if message != "":
            handle_message(message, index)
            index += 1
        message = ""
#################################사진 메타정보 확인 과정########################################

def lat_lon_to_addr(lon, lat):
    url = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={longitude}&y={latitude}'.format(longitude=lon, latitude=lat)
    headers = {"Authorization": "KakaoAK " + api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        match_first = result['documents'][0]['address_name']
        return match_first
    else:
        return "No Data"

api_key = "20e841d134e90cd157222ba545984e63"

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


def image_info_to_db(info):

    # date
    make_time = info.get(36867)
    print("촬영 시간:", make_time if make_time else "정보 없음")
    
    # season
    month = make_time[5:7] if make_time else None
    image_weather = season_list[month] if month else "정보 없음"
    print("날씨:", image_weather)

    # gps(lat, lon)
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

    print("위도 경도:", (lat, lon) if (lat and lon) else "정보 없음")
    print("주소:", address)

    return image_weather, make_time, (lat, lon), address








if __name__ == "__main__":
    listen_for_messages()