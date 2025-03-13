#!/usr/bin/env python3
import jetson.inference
import jetson.utils

# 네트워크 초기화
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

# 비디오 소스 초기화 (CSI 카메라 또는 V4L2 웹캠)
camera = jetson.utils.videoSource("csi://0")  # CSI 카메라 사용 예시

# 비디오 출력을 사용하지 않음
# display = jetson.utils.videoOutput("display://0")  # 주석 처리

while True:
    img = camera.Capture()  # 카메라에서 이미지 캡처
    detections = net.Detect(img)  # 이미지에서 객체 감지

    # 가장 큰 객체 찾기
    largest_area = 0
    largest_center_x = 0
    for detection in detections:
        area = detection.Width * detection.Height  # 객체의 면적 계산
        if area > largest_area:
            largest_area = area
            # 객체 중심 좌표 계산
            largest_center_x = detection.Center[0]

    # 화면 중앙 좌표 계산
    screen_center_x = img.width / 2

    # 화면 중앙으로부터 객체 중심까지의 거리 계산
    distance_from_center = largest_center_x - screen_center_x

    # 상태 메시지 출력
    status_message = "Object Detection | Network {:.0f} FPS | Distance from Center: {:.2f}".format(net.GetNetworkFPS(), distance_from_center)
    print(status_message)
