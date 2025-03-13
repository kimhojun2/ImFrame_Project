
import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(2)

with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("웹캠을 찾을 수 없습니다.")
            break

        # 이미지 좌우 반전 및 BGR에서 RGB로 변환
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_detection.process(image)

        # 원본 이미지로 돌려놓기
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        h, w, _ = image.shape
        largest_area = 0
        largest_detection = None

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                area = bboxC.width * bboxC.height
                if area > largest_area:
                    largest_area = area
                    largest_detection = detection

            if largest_detection:
                bbox = largest_detection.location_data.relative_bounding_box
                x_center = int((bbox.xmin + bbox.width / 2) * w)
                center_of_webcam = w // 2

                # 중심 좌표와 웹캠 중심과의 X 좌표 거리 계산
                distance_x = center_of_webcam - x_center

                print(f"Distance from Center{distance_x}")

                if abs(distance_x) >= 30:
                    # 거리에 따른 모터 회전 각도 계산 (예시: 각도 = 거리 / 10)
                    rotation_angle = distance_x / 10
                    print(f"{rotation_angle} 도 ")

                # 가장 큰 객체 감지 박스 그리기
                mp_drawing.draw_detection(image, largest_detection)

        # 결과 보여주기 - 이 부분을 주석 처리
       
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
# cv2.destroyAllWindows()  # 이 부분도 필요 없으므로 주석 처리
