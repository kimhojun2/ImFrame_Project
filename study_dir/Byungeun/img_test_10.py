#!/usr/bin/env python3
import jetson.inference
import jetson.utils
import time

def main():
    # 네트워크 및 카메라 초기화
    net = jetson.inference.detectNet("facenet-120", threshold=0.1)
    camera = jetson.utils.videoSource("csi://0")  # CSI 카메라 사용

    num_detections = 0  # 인식된 객체의 수를 카운트

    for i in range(10):  # 10회 반복
        img = camera.Capture()
        detections = net.Detect(img)

        # 인식 결과를 이미지에 박싱
        for detection in detections:
            print(f"Detected object: {net.GetClassDesc(detection.ClassID)} with confidence {detection.Confidence}")
            jetson.utils.cudaDrawRect(img, detection.ROI, (255, 0, 0, 150))  # 빨간색 박스

        # 이미지 파일로 저장
        image_filename = f"detected_frame_{i+1}.jpg"
        jetson.utils.saveImageRGBA(image_filename, img, img.width, img.height)
        print(f"Detection completed and image saved as '{image_filename}'.")

        # 인식된 객체가 있으면 카운트 증가
        if len(detections) > 0:
            num_detections += 1

        time.sleep(1)  # 카메라 캡쳐 사이에 약간의 지연을 줍니다.

    print(f"Total successful detections: {num_detections} out of 10")

if __name__ == "__main__":
    main()
