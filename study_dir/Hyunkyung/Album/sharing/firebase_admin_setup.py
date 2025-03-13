#firebase_admin_setup.py
import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import firestore

def initialize_firebase():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Firebase Admin SDK JSON 파일 경로
    cred_path = os.path.join(dir_path, 'ifind-firebase-adminsdk.json')
    cred = credentials.Certificate(cred_path)

    # Firebase 앱 초기화
    firebase_admin.initialize_app(cred)
    print("Firebase Admin Initialized")

def get_firestore_client():
    # Firestore 클라이언트 가져오기
    return firestore.client()

if __name__ == '__main__':
    # Firebase 초기화
    initialize_firebase()

    # Firestore 연결 확인
    # db = get_firestore_client()
    # docs = db.collection('users').limit(10).stream()

    # for doc in docs:
    #     print(f'{doc.id} => {doc.to_dict()}')
