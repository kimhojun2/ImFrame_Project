#group_photo_set_up.py
import os
import sys
import threading
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import time
# import json
import requests
from io import BytesIO
from firebase_admin_setup import initialize_firebase, get_firestore_client

def read_uid_file(file_path):
    """ 파일에서 UID를 읽기 """
    with open(file_path, 'r') as file:
        return file.read().strip()

# 시간마다 확인해서 json파일로 저장
# def write_image_urls(file_path, image_urls):
#     with open(file_path, 'w') as file:
#         json.dump(image_urls, file)

#firebase snapshot 이용

# 스냅샷
# def on_group_image_change(doc_snapshot, changes, read_time):
#     """ 그룹의 img_url 변경 감지 시 동작할 콜백 함수 """
#     for change in changes:
#         if change.type == 'modified':
#             new_img_url = change.document.to_dict().get('img_url')
#             group_id = change.document.id
#             print(f"그룹 '{group_id}'의 img_url 변경됨: {new_img_url}")
#     callback_done.set()

# def monitor_group_images(group_name):
#     """ 각 그룹별 img_url 필드를 실시간 조회 """
#     db = get_firestore_client()
#     group_doc = db.collection('group').document(group_name)
#     print(f"Listening for changes on group document: {group_name}")
#     group_doc.on_snapshot(
#         lambda doc_snapshot, changes, read_time: on_group_image_change(doc_snapshot, changes, read_time)
#     )
class ImageDisplay(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Group Image Display')
        self.setScaledContents(True)
        self.showFullScreen()  # 전체 화면으로 표시
        self.setAttribute(Qt.WA_DeleteOnClose, True)  # 창이 닫힐 때 위젯 삭제

    def load_image_from_url(self, img_url):
        """URL에서 이미지를 로드하고 표시합니다."""
        response = requests.get(img_url)
        img_data = BytesIO(response.content)
        pixmap = QPixmap()
        pixmap.loadFromData(img_data.getvalue())
        self.setPixmap(pixmap)
        self.showFullScreen()  # 이미지 로딩 후 전체 화면으로 표시
        self.show()
        
    def mousePressEvent(self, event):
        self.close()  # 이미지 클릭 시 프로그램 종료
        
# def show_image(img_url):
#     global display
#     pixmap = QPixmap(img_url)
#     display.setPixmap(pixmap)
#     display.show()

def on_document_written(doc_snapshot, changes, read_time):
    """문서가 작성되거나 수정될 때 호출되는 콜백 함수"""
    for doc in doc_snapshot:
        new_img_url = doc.to_dict().get('img_url', None)
        if new_img_url:
            group_id = doc.id
            print(f"그룹 '{group_id}'의 img_url이 변경되었습니다: {new_img_url}")
            display.load_image_from_url(new_img_url)

def monitor_group_images(group_name):
    db = get_firestore_client()
    group_doc = db.collection('group').document(group_name)
    group_doc.on_snapshot(on_document_written)

def fetch_user_groups(uid):
    db = get_firestore_client()
    user_doc = db.collection('users').document(uid)
    doc = user_doc.get()
    if doc.exists:
        groups = doc.to_dict().get('groups', [])
        for group_name in groups:
            monitor_group_images(group_name)
    else:
        print(f"No user found with UID {uid}")

# img_url 필드 조회 로직
# def fetch_user_groups(uid):
#     """ UID의 Firestore에서 'users' 컬렉션의 'groups' 필드를 조회"""
#     db = get_firestore_client()
#     user_doc = db.collection('users').document(uid)
#     image_urls = []
#     try:
#         doc = user_doc.get()
#         if doc.exists:
#             groups = doc.to_dict().get('groups', [])
#             if groups:
#                 image_urls = fetch_group_images(db, groups)
#             else:
#                 print("No groups found for this user.")
#         else:
#             print(f"No user found with UID {uid}")
#     except Exception as e:
#         print(f"An error occurred while fetching user groups: {e}")
#     return image_urls

# def fetch_group_images(db, groups):
#     """ 각 그룹의 'img_url'을 조회 """
#     img_urls = {}
#     for group in groups:
#         group_doc = db.collection('group').document(group)
#         try:
#             doc = group_doc.get()
#             if doc.exists:
#                 img_url = doc.to_dict().get('img_url', None)
#                 if img_url:
#                     img_urls[group] = img_url
#             else:
#                 print(f"No details found for group '{group}'")
#         except Exception as e:
#             print(f"img_url을 가져오는데 실패했습니다. '{group}': {e}")
#     return img_urls

if __name__ == '__main__':
    initialize_firebase()
    uid_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uid.txt')
    uid = read_uid_file(uid_file_path)
    if uid:
        app = QApplication(sys.argv)
        display = ImageDisplay()
        fetch_user_groups(uid)
        display.show()
        sys.exit(app.exec_()) # 이벤트 루프 시작