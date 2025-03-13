#invoke_stt.py

import speech_recognition as sr
import subprocess
import sys
import os

def listen_for_activation_word(activation_word="어이"):
    """지속적으로 마이크 입력을 받아 특정 단어를 감지합니다."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("마이크를 듣고 있습니다...")

    while True:
        try:
            with microphone as source:
                audio = recognizer.listen(source)
            # Google Speech Recognition을 사용해 오디오를 텍스트로 변환
            text = recognizer.recognize_google(audio, language='ko-KR')
            print(f"인식된 텍스트: {text}")

            # 특정 단어가 감지되면 STT.py 실행
            if activation_word in text:
                print(f"트리거 단어 '{activation_word}' 감지됨. STT.py를 실행합니다.")
                current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 디렉토리 절대 경로
                stt_path = os.path.join(current_dir, 'STT.py')
                # STT.py 스크립트 실행
                subprocess.run(['python', stt_path])
                
        except sr.UnknownValueError:
            print("Google Speech Recognition이 이해할 수 없음")
        except sr.RequestError as e:
            print(f"Google Speech Recognition 서비스에 요청 실패; {e}")

if __name__ == "__main__":
    listen_for_activation_word()
