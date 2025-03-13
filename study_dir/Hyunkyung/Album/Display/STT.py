#STT.py
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import requests
import io
# from nltk.tokenize import word_tokenize
# import spacy
# from transformers import pipeline
import konlpy
from konlpy.tag import Okt
from krwordrank.word import KRWordRank
# import dateparser
# from google.cloud import vision
from dateutil import parser
from datetime import datetime
import json
import re
import sqlite_utils
import cv2
import sys
import speech_recognition as sr
import subprocess
import time
import os
import threading
# import torch



class SpeechToText:
    def __init__(self):
        # 네이버 클로바 API 정보
        self.client_id = "vh65ko3r7j"
        self.client_secret = "3SRnacV8fqpfFGsmIlYaIgJDce9H1NytIfs4Hl2j"
        self.fs = 16000  # 샘플링 레이트
        self.duration = 5  # 녹음할 시간 (초)

    def record_audio(self):
        print("녹음을 시작합니다...")
        recording = sd.rec(int(self.duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
        sd.wait()
        print("녹음이 완료되었습니다.")
        return recording

    def send_audio_to_stt(self, audio_data):
        """녹음된 오디오를 Clova STT API로 전송하고 결과를 출력합니다."""
        lang = "Kor"
        url = f"https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang={lang}"
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
            text = response.json()['text']
            print("인식 결과:", text)
            return text
        else:
            print("Error:", response.text)
            return None
        
    def continuous_listen(self, keyword_finder):
        while True:
            audio_data = self.record_audio()
            recognized_text = self.send_audio_to_stt(audio_data)
            if recognized_text:
                keyword_finder.extract_keywords(recognized_text)
                date = keyword_finder.parse_date_from_text(recognized_text)
                place = keyword_finder.extract_regions(recognized_text)
                if date or place:
                    keywords = [date, place]
                    keyword_finder.find_image(keywords)
                else:
                    print("검색결과 없음")
            time.sleep(5)

class GoogleVoiceCommand:
    def __init__(self):
        self.activation_words = {
            "나가": self.exit_program,
            "다음": self.next_action,
            "이전": self.previous_action
        }

    def exit_program(self):
        print("프로그램을 종료합니다.")
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 디렉토리 절대 경로
        stt_path = os.path.join(current_dir, 'invoke_stt.py')
        subprocess.call(["python", stt_path])
        sys.exit()

    def next_action(self):
        print("다음 페이지 로직 수행")
        # 다음 페이지 로직 구현

    def previous_action(self):
        print("이전 페이지 로직 수행")
        # 이전 페이지 로직 구현

    def listen(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Google STT 활성화, 마이크를 듣고 있습니다...")
        while True:
            try:
                with microphone as source:
                    audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio, language='ko-KR')
                print(f"인식된 명령어: {command}")
                for word, action in self.activation_words.items():
                    if word in command:
                        action()
                        break
            except sr.UnknownValueError:
                print("Google STT가 이해할 수 없음")
            except sr.RequestError as e:
                print(f"Google STT 서비스에 요청 실패: {e}")


class KeywordFinder:
    def __init__(self):
        self.korean_regions = [
            "강남", "서초", "종로", "명동", "이태원", "동대문", "홍대", "신촌", "이화", "서대문", "마포",
            "용산", "성동", "광진", "중랑", "성북", "강북", "도봉", "노원", "은평", "양천", "강서",
            "구로", "금천", "영등포", "동작", "관악", "송파", "강동", "해운대", "동래", "부산진",
            "남구", "서구", "영도", "부산", "인천", "미추홀", "연수", "남동", "부평", "계양", "경주",
            "전주", "광주", "대전", "울산", "세종", "수원", "성남", "고양", "용인", "부천", "청주", "안산",
            "제주", "포항", "창원", "강릉", "강원도", "역삼", "송도", "광명", "김포", "잠실", "용인", "주문진", "보성", "서울",
        ]
    def extract_keywords(self, text):
        # # 텍스트를 처리
        # doc = nlp(text)
        # keywords = []

        # # 명사와 명사구 추출
        # for chunk in doc.noun_chunks:
        #     keywords.append(chunk.text)

        # # 중복 제거
        # keywords = list(set(keywords))
        # print(keywords)
        
        okt = Okt()
        nouns = okt.nouns(text)  # 명사 추출
        print("Extracted Keywords:", nouns)
        
    # def extract_date(text):
    #     entities = nlu(text)
    #     dates = [entity['word'] for entity in entities if entity['entity'] == 'DATE']
    #     return dates

    # def extract_location(text):
    #     nlp = spacy.load('en_core_web_sm')
    #     doc = nlp(text)
    #     locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    #     return locations

    # def send_message_to_chatbot(text, api_url, api_key):
    #     headers = {
    #         'Content-Type': 'application/json; charset=utf-8',
    #         'X-NCP-CHATBOT_SIGNATURE': api_key
    #     }
        
    #     # 챗봇 API에 보낼 요청 데이터
    #     data = {
    #         'version': 'v2',
    #         'userId': 'example_user',
    #         'timestamp': 0,
    #         'bubbles': [{
    #             'type': 'text',
    #             'data': {
    #                 'description': text
    #             }
    #         }],
    #         'event': 'send'
    #     }
        
    #     # JSON 형식으로 데이터를 변환하여 요청 보내기
    #     response = requests.post(api_url, headers=headers, data=json.dumps(data))
    #     if response.status_code == 200:
    #         try:
    #             return response.json()
    #         except json.JSONDecodeError:
    #             print("JSON decoding failed:", response.text)
    #             return None
    #     else:
    #         print("Failed to send message:", response.status_code, response.text)
    #         return None
        
    def parse_date_from_text(self, text):
        now = datetime.now()
        current_year = now.year

        # 년, 월, 일
        full_date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', text)
        if full_date_match:
            year = int(full_date_match.group(1))
            month = int(full_date_match.group(2))
            day = int(full_date_match.group(3))
            return f"{year}:{month:02d}:{day:02d}"

        # 년, 월
        year_month_match = re.search(r'(\d{4})년\s*(\d{1,2})월', text)
        if year_month_match:
            year = int(year_month_match.group(1))
            month = int(year_month_match.group(2))
            return f"{year}:{month:02d}"

        # 년도
        year_match = re.search(r'(\d{4})년', text)
        if year_match:
            year = int(year_match.group(1))
            return str(year)

        # 작년,재작년
        relative_year_month_match = re.search(r'(작년|재작년)\s*(\d{1,2})월', text)
        if relative_year_month_match:
            relative_term = relative_year_month_match.group(1)
            month = int(relative_year_month_match.group(2))
            year = current_year - 1 if relative_term == '작년' else current_year - 2
            return f"{year}:{month:02d}"

        # "작년", "재작년" 단독으로 사용된 경우
        if '작년' in text:
            return f"{current_year - 1}"
        if '재작년' in text:
            return f"{current_year - 2}"

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
                conditions.append(f"date LIKE '%{keyword}%'")
            elif idx == 1 and keyword is not None:
                conditions.append(f"address LIKE '%{keyword}%'")

        if not conditions:
            print("올바른 키워드를 입력하세요.")
            return

        query = "SELECT * FROM album WHERE " + " AND ".join(conditions)

        # 데이터베이스에서 검색
        results = db.query(query)  # 제너레이터

        if results:
            print("검색 결과:")
            for idx, result in enumerate(results, start=1):
                print(f"{idx}. Title: {result['title']}, Address: {result['address']}, Weather: {result['season']}, Location: {result['gps']}, Date: {result['date']}")
                image_p = result['image']
                
                image = cv2.imread(image_p)
                re_size_image = cv2.resize(image, (500, 500))
                
                cv2.namedWindow('result', cv2.WINDOW_NORMAL)  # 창 크기 조정 가능하도록 지정
                cv2.setWindowProperty('result', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  # 전체 화면으로 설정
                
                cv2.imshow('result', re_size_image)
                key = cv2.waitKey(0)
                
                if key == 32:  # 스페이스바가 눌렸을 때
                    pass  # 아무것도 하지 않음. 다음 결과를 처리할 것임
                elif key == 27:  # ESC 키가 눌렸을 때
                    break  # 종료
            
            cv2.destroyAllWindows()  # 모든 창 닫기
        else:
            print("검색 결과가 없습니다.")
            

if __name__ == "__main__":
    stt = SpeechToText()
    kf = KeywordFinder()
    gvc = GoogleVoiceCommand()
    
    stt_thread = threading.Thread(target=stt.continuous_listen, args=(kf,))
    stt_thread.start()
    
    gvc.listen()
    stt_thread.join()