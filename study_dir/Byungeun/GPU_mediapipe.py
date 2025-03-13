import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(2)

with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # CUDA를 사용하여 GPU 메모리에 이미지를 업로드
        cuda_frame = cv2.cuda_GpuMat()  # CUDA 메모리를 위한 객체 생성
        cuda_frame.upload(frame)  # 읽은 프레임을 CUDA 객체에 업로드

        # CUDA를 사용하여 이미지를 RGB로 변환
        image_rgb = cv2.cuda.cvtColor(cuda_frame, cv2.COLOR_BGR2RGB)
        image_rgb = image_rgb.download()  # MediaPipe 처리를 위해 CPU 메모리로 다운로드

        # MediaPipe 얼굴 인식 처리
        results = face_detection.process(image_rgb)

        if results.detections:
            h, w, _ = frame.shape
            center_of_webcam = (w // 2, h // 2)

            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                x_center = int((bboxC.xmin + bboxC.width / 2) * w)
                y_center = int((bboxC.ymin + bboxC.height / 2) * h)

                # 중심 좌표와 웹캠 중심과의 거리 계산
                distance_x = center_of_webcam[0] - x_center
                distance_y = center_of_webcam[1] - y_center
                print(f"Face center: ({x_center}, {y_center})")
                print(f"Distance from Center: X={distance_x}, Y={distance_y}")

                # 가장 큰 객체 감지 박스 그리기 (선택적)
                mp_drawing.draw_detection(image_rgb, detection)

        # 결과 보여주기 (디버깅용, 실제 사용시 주석 처리)
        

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
