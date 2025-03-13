import pymongo

# MongoDB에 연결
client = pymongo.MongoClient("mongodb://localhost:27017/")

# 데이터베이스 선택 (없으면 새로 생성)
db = client["local_db"]

# collection 생성
collection = db["album"]

# 필드 정의
fields = {
    "title": str,
    "image": str,
    "season": str,
    "date": str,
    "gps": tuple,
    "address": str
}

# collection에 필드 추가
collection.insert_one(fields)
