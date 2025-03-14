#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#STT.py
from PyQt5.QtCore import QObject
from PyQt5 import  QtWidgets, QtCore
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import requests
import io
from datetime import datetime
import re
import sqlite_utils
import cv2
import sys
import time
from queue import Queue
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel

class SpeechToText(QtCore.QObject):
    image_signal = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    restart_listener = QtCore.pyqtSignal()
    def __init__(self, on_complete=None, device_index=12):
        super().__init__()
        self.on_complete = on_complete
        self.running = True
        # 네이버 클로바 API 정보
        self.client_id = "vh65ko3r7j"
        self.client_secret = "3SRnacV8fqpfFGsmIlYaIgJDce9H1NytIfs4Hl2j"
        self.fs = 48000  # 샘플링 레이트
        self.duration = 5  # 녹음할 시간 (초)
        self.missed_count = 0  # 연속으로 인식 실패한 횟수
        self.max_misses = 2  # 최대 허용 실패 횟수
        self.device_index = device_index
        self.stream = None
        self.queue = Queue()
        self.korean_regions = [
            "강남", "서초", "종로", "명동", "이태원", "동대문", "홍대", "신촌", "이화", "서대문", "마포",
            "용산", "성동", "광진", "중랑", "성북", "강북", "도봉", "노원", "은평", "양천", "강서",
            "구로", "금천", "영등포", "동작", "관악", "송파", "강동", "해운대", "동래", "부산진",
            "남구", "서구", "영도", "부산", "인천", "미추홀", "연수", "남동", "부평", "계양", "경주",
            "전주", "광주", "대전", "울산", "세종", "수원", "성남", "용인", "부천", "청주", "안산",
            "제주", "포항", "창원", "강릉", "강원도", "역삼", "송도", "광명", "김포", "잠실", "용인", "주문진", "보성", "서울",
        ]
        self.object_list = [
            "자전거", "자동차", "오토바이", "비행기", "버스", "기차", "트럭", "보트",
            "신호등", "소화전", "도로 표지판", "정지 표지판", "주차 미터기", "벤치",
            "새", "고양이", "개", "말", "소", "코끼리", "곰", "얼룩말", "기린",
            "모자", "배낭", "우산", "신발", "안경", "핸드백", "넥타이", "여행가방",
            "프리스비", "스키", "스노우보드", "스포츠 공", "연", "야구 배트",
            "야구 글러브", "스케이트보드", "서핑보드", "테니스 라켓",
            "병", "접시", "와인 잔", "컵", "포크", "나이프", "숟가락", "그릇",
            "바나나", "사과", "샌드위치", "오렌지", "브로콜리", "당근", "핫도그", "피자", "도넛", "케이크",
            "의자", "소파", "화분", "침대", "거울", "식탁", "창문", "책상", "화장실", "문",
            "TV", "노트북", "마우스", "리모컨", "키보드", "휴대폰", "전자레인지", "오븐", "토스터", "싱크대", "냉장고", "믹서기",
            "책", "시계", "꽃병", "가위", "테디 베어", "헤어 드라이어", "칫솔"
        ]
    
    def run(self):
        while self.running and self.missed_count < self.max_misses:
            audio_data = self.record_audio()
            recognized_text = self.send_audio_to_stt(audio_data)
            if recognized_text:
                keywords = self.extract_keywords(recognized_text)
                if keywords:
                    self.find_image(keywords)
                else:
                    print("검색 결과가 없습니다.")
            else:
                self.missed_count += 1
                if self.missed_count >= self.max_misses:
                    print("2회 연속 대화 없음으로 프로그램을 종료합니다.")
                    self.running = False
                    self.exit_program()
            time.sleep(5)
        self.finished.emit()
        # self.exit_program()
    

    def record_audio(self):
        print("녹음을 시작합니다...")
        recording = sd.rec(int(self.duration * self.fs), samplerate=self.fs, channels=1, dtype='int16', device=self.device_index)
        sd.wait()
        print("녹음이 완료되었습니다.")
        return recording

    def send_audio_to_stt(self, audio_data):
        """녹음된 오디오를 Clova STT API로 전송하고 결과를 출력합니다."""
        lang = "Kor"
        url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang={}".format(lang)
        headers = {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret,
            "Content-Type": "application/octet-stream"
        }
        bio = io.BytesIO()
        write(bio, self.fs, audio_data.astype(np.int16))
        bio.seek(0)
        response = requests.post(url, data=bio.read(), headers=headers)
        bio.close()
        
        if response.status_code == 200:
            json_response = response.json()
            text = json_response.get('text', '')
            if text:
                print("인식 결과:", text)
                self.extract_control(text)  # 종료 로직 호출
                self.extract_smartthings(text)  # 스마트싱스 제어 로직 호출
                self.missed_count = 0
                return text
            else:
                print("인식된 것 없음")
                self.missed_count += 1
                return None
        else:
            print("Error:", response.text)
            self.missed_count += 1
            return None
    
    #앨범 제어 로직
    def extract_control(self, text):
        if '종료' in text or '나가' in text:
            print("종료 키워드가 감지되었습니다. 처리 중...")
            # 종료 전 필요한 작업을 처리하도록 설정
            self.running = False
            self.exit_program()
            
            # if self.on_complete:
            #     self.on_complete()
            # else:
            #     self.exit_program()
    
    #스마트 싱스 제어 로직
    def extract_smartthings(self, text):
        if '싱스' in text or '씽스' in text or '심스' in text:
            print("스마트싱스로직")


    def extract_keywords(self, text):
        keywords = [None, None, None]  # 날짜, 지역, 객체 순서로 초기화

    # 날짜 정보 추출
        date_info = self.parse_date_from_text(text)
        if date_info:
            keywords[0] = date_info
        
        # 지역명 검색
        for region in self.korean_regions:
            if region in text:
                keywords[1] = region
                break  # 첫 번째 일치하는 지역을 찾으면 중단
        
        # 객체 검색
        for object in self.object_list:
            if object in text:
                keywords[2] = object
                break  # 첫 번째 일치하는 객체를 찾으면 중단
        
        print(keywords)
        return keywords
        
    
    def parse_date_from_text(self, text):
            now = datetime.now()
            current_year = now.year

            # 년, 월, 일
            full_date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', text)
            if full_date_match:
                year = int(full_date_match.group(1))
                month = int(full_date_match.group(2))
                day = int(full_date_match.group(3))
                return "{year}:{month:02d}:{day:02d}".format(year=year, month=month, day=day)

            # 년, 월
            year_month_match = re.search(r'(\d{4})년\s*(\d{1,2})월', text)
            if year_month_match:
                year = int(year_month_match.group(1))
                month = int(year_month_match.group(2))
                return "{year}:{month:02d}".format(year=year, month=month)

            # 년도
            year_match = re.search(r'(\d{4})년', text)
            if year_match:
                year = int(year_match.group(1))
                return str(year)

            # 작년,재작년
            relative_year_month_match = re.search(r'(올해|작년|재작년)\s*(\d{1,2})월', text)
            if relative_year_month_match:
                relative_term = relative_year_month_match.group(1)
                month = int(relative_year_month_match.group(2))
                year = current_year - 1 if relative_term == '작년' else current_year - 2
                return "{year}:{month:02d}".format(year=year, month=month)

            # "작년", "재작년" 단독으로 사용된 경우
            if '올해' in text:
                return str(current_year)
            if '작년' in text:
                return str(current_year - 1)
            if '재작년' in text:
                return str(current_year - 2)

            return None

    def extract_regions(self, text):
        for region in self.korean_regions:
            if re.search(region, text):
                return region
        return None

    def find_image(self, keywords):
        # SQLite 연결
        db = sqlite_utils.Database("local.db")
        
        # 쿼리 구성
        conditions = []
        for idx, keyword in enumerate(keywords):
            if idx == 0 and keyword is not None:
                conditions.append("date LIKE '%{keyword}%'".format(keyword=keyword))
            elif idx == 1 and keyword is not None:
                conditions.append("address LIKE '%{keyword}%'".format(keyword=keyword))
            elif idx == 2 and keyword is not None:
                conditions.append("tags LIKE '%{keyword}%'".format(keyword=keyword))

        if not conditions:
            print("올바른 키워드를 입력하세요.")
            return

        query = "SELECT * FROM album WHERE " + " AND ".join(conditions)

        # 데이터베이스에서 검색
        results = db.query(query) if query else []  # 제너레이터

        if results:
            print("검색 결과:")
            for result in results:
                image_path = result['image']
                print(image_path)
                self.image_signal.emit(image_path)
                print("경로생성완료")
                self.stop()
                break
            # cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
            # cv2.setWindowProperty('Result', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #     for idx, result in enumerate(results, start=1):
        #         print("{idx}. Title: {title}, Address: {address}, Weather: {weather}, Location: {location}, Date: {date}".format(
        #             idx=idx,
        #             title=result['title'],
        #             address=result['address'],
        #             weather=result['season'],
        #             location=result['gps'],
        #             date=result['date'],
        #             # tags=result['tags']
        # ))
        #         image_p = result['image']
                
        #         image = cv2.imread(image_p)
        #         if image is not None:
        #             cv2.imshow('Result',  image)
        #             cv2.waitKey(5000)  # 이미지를 5초간 표시
        #             cv2.destroyAllWindows()
        #             self.exit_program()
                
        #         key = cv2.waitKey(0)
                
        #         if key == 32:  # 스페이스바가 눌렸을 때
        #             pass  # 아무것도 하지 않음. 다음 결과를 처리할 것임
        #         elif key == 27:  # ESC 키가 눌렸을 때
        #             break  # 종료
            
        #     cv2.destroyAllWindows()  # 모든 창 닫기
        else:
            print("검색 결과가 없습니다.")
            
    def stop(self):
        self.running = False
        self.finished.emit()
        print(1)
        self.restart_listener.emit()
    
    def exit_program(self):
        print("STT processing complete. Exiting...")
        self.stop()
        sys.exit()
        
    def cleanup(self):
        try:
            self.recorder.stop()
            self.recorder.delete()
        except Exception as e:
            print(f"Failed to stop or delete recorder: {e}")
        try:
            self.porcupine.delete()
        except Exception as e:
            print(f"Failed to delete Porcupine instance: {e}")

if __name__ == "__main__":

    # stt = SpeechToText(on_complete=lambda: print("Cleanup complete"))
    # stt.run()
    app = QtWidgets.QApplication(sys.argv)
    stt_instance = SpeechToText()
    from viewer import DisplayImage
    display_instance = DisplayImage()  # DisplayImage 인스턴스 생성
    stt_instance = SpeechToText()
    stt_instance.image_signal.connect(display_instance.display_image)  # 신호 연결
    stt_instance.run()  # STT 실행
    sys.exit(app.exec_())