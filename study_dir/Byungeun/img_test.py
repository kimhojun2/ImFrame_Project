#!/usr/bin/env python3
import jetson.inference
import jetson.utils

def main():
    # 네트워크 및 카메라 초기화
    net = jetson.inference.detectNet("facenet-120", threshold=0.5)
    camera = jetson.utils.videoSource("csi://0")  # CSI 카메라 사용
    
    # 이미지 캡쳐
    img = camera.Capture()
    
    # 객체 인식
    detections = net.Detect(img)
    
    # 인식 결과를 이미지에 박싱
    for detection in detections:
        print(f"Detected object: {net.GetClassDesc(detection.ClassID)} with confidence {detection.Confidence}")
        jetson.utils.cudaDrawRect(img, detection.ROI, (255, 0, 0, 150))  # 빨간색 박스

    # 이미지 파일로 저장
    jetson.utils.saveImageRGBA("detected_frame.jpg", img, img.width, img.height)

    print("Detection completed and image saved as 'detected_frame.jpg'.")

if __name__ == "__main__":
    main()
