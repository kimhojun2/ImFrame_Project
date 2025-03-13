import pvporcupine
import pyaudio
import struct

import os

def wake_word_detection(access_key):
    porcupine = None
    pa = None
    audio_stream = None

    try:
        # 파일 이름을 포함한 경로를 설정
        current_dir = os.path.dirname(os.path.realpath(__file__))
        print("Current working directory:", current_dir)
        keyword_path = os.path.join(current_dir, 'next_ko_windows_v3_0_0')

        porcupine = pvporcupine.create(access_key=access_key, keyword_paths=[keyword_path])
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for wake words...")

        while True:
            pcm_frame = audio_stream.read(porcupine.frame_length)
            pcm_int16 = struct.unpack_from("h" * porcupine.frame_length, pcm_frame)

            if porcupine.process(pcm_int16):
                print("Detected wake word!")
                # 여기에서 추가 작업을 트리거할 수 있습니다.

    except KeyboardInterrupt:
        print("Stopping")
    finally:
        if porcupine is not None:
            porcupine.delete()

        if audio_stream is not None:
            audio_stream.close()

        if pa is not None:
            pa.terminate()

# 액세스 키를 실제 Picovoice 액세스 키로 교체하세요.
wake_word_detection(access_key='AlYKGy/vGuk1r+mLzKUmeQ/aUrnDGJdwan97wtLvdcAnAmsj1GNP+w==')