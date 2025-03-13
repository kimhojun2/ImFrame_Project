from PIL import Image
from PIL.ExifTags import TAGS
import requests
import sqlite_utils

db = sqlite_utils.Database("local.db")

def lat_lon_to_addr(lon, lat):
    url = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={longitude}&y={latitude}'.format(longitude=lon, latitude=lat)
    headers = {"Authorization": "KakaoAK " + api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        match_first = result['documents'][0]['address_name']
        return match_first
    else:
        return "Something went wrong!"

api_key = "20e841d134e90cd157222ba545984e63"

season = {'01':'겨울',
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

image = Image.open(r'cat.jpg')
info = image._getexif()  # 이미지 메타정보

make_time = info.get(36867)  # 이미지 촬영 시간 정보 추출
month = make_time[5:7] if make_time else None
image_weather = season[month] if month else "정보 없음"
print("날씨:", image_weather)

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

print("월:", month if month else "정보 없음")
print("촬영 시간:", make_time if make_time else "정보 없음")
print("위도 경도:", (lat, lon) if (lat and lon) else "정보 없음")
print("주소:", address)


data = {
    "title": "cat.jpg",
    "image": "./album/cat.jpg",
    "season": image_weather,
    "date": make_time,
    "gps": (lat, lon),
    "address": address
}

db["album"].insert(data)