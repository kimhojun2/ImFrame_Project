from ultralytics import YOLO
import numpy as np
import cv2

# 모터 제어를 위한 함수, 필요에 따라 하드웨어에 맞게 구현
def rotate_camera(direction, degrees):
    if direction == 'left':
        print(f"Rotate camera left by {degrees} degrees")
    elif direction == 'right':
        print(f"Rotate camera right by {degrees} degrees")

# YOLO 모델 로드
model = YOLO("yolov8n.pt")

# 객체 추적 및 인식 시작
result = model.track(source=0, show=True, tracker="bytetrack.yaml", classes=0)

try:
    while True:
        # 결과를 처리하여 객체의 중앙값을 기준으로 화면 중앙에서 얼마나 벗어났는지 계산
        if len(result.xyxy) > 0:
            # 객체 박스의 중앙값 계산
            box = result.xyxy[0][0]  # 첫 번째 객체의 박스
            box_center_x = (box[0] + box[2]) / 2
            
            # 화면의 중앙값 계산
            frame_width = result.imgs.shape[1]  # 이미지 너비
            frame_center = frame_width // 2
            
            # 화면 중앙과 객체 중앙 간의 거리 계산
            distance_from_center = frame_center - box_center_x
            
            # 중앙값을 기준으로 객체가 화면 중앙에서 벗어난 거리 출력
            print(f"Distance from center: {distance_from_center}")
        
        # ESC 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    cv2.destroyAllWindows()
