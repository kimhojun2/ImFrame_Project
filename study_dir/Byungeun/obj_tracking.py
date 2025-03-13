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

# 비디오 캡쳐 객체 초기화
cap = cv2.VideoCapture(0)

# 화면 중앙 값 계산
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_center = frame_width // 2

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 프레임을 YOLO 모델에 입력
        results = model.predict(frame, classes=[0])  # 클래스 0은 'person'
        
        # 검출된 객체 중 가장 큰 객체 사용
        detections = results.pandas().xyxy[0]  # 결과를 Pandas DataFrame으로 변환
        if not detections.empty:
            # 가장 큰 객체를 찾습니다.
            largest_object = detections.loc[detections['area'].idxmax()]
            
            # 객체의 중심 좌표 계산
            x_center = (largest_object['xmin'] + largest_object['xmax']) / 2
            
            # 카메라의 중심과 객체의 중심 사이의 차이 계산
            error = frame_center - x_center
            
            # 에러에 따라 카메라 회전
            if abs(error) > frame_width * 0.1:  # 중심 차이가 전체 너비의 10% 이상일 경우 조정
                if error > 0:
                    rotate_camera('left', abs(error) // frame_width * 10)  # 회전 각도는 오차에 비례
                else:
                    rotate_camera('right', abs(error) // frame_width * 10)
        
        # 결과를 화면에 표시
        cv2.imshow('YOLO v8 Detection', np.squeeze(results.render()))
        
        # ESC 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
