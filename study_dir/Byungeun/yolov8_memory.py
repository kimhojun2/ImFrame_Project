from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")  # 클래스 0만 추적

cap = cv2.VideoCapture(0)  # 웹캠 사용
if not cap.isOpened():
    print("Camera could not be opened.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 각 프레임에 대해 객체 추적 실행
    results = model.track(frame, tracker="bytetrack.yaml", classes=0)

    # 결과 표시 또는 기타 처리
    results.show()  # 결과를 화면에 표시
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키로 루프 탈출
        break

cap.release()
cv2.destroyAllWindows()
