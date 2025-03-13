import cv2
from cvzone.FaceDetectionModule import FaceDetector
import numpy as np

cap = cv2.VideoCapture(0)
ws, hs = 900, 600
cap.set(3, ws)
cap.set(4, hs)

if not cap.isOpened():
    print("Camera couldn't access!!!")
    exit()

detector = FaceDetector()
servoPos = [90, 90]  # 서보 모터 위치 (가상)

while True:
    success, img = cap.read()
    if not success:
        break
    
    img, bboxs = detector.findFaces(img, draw=False)  # 얼굴 감지
    
    if bboxs:
        # 얼굴 중심 좌표 가져오기
        fx, fy = bboxs[0]["center"][0], bboxs[0]["center"][1]
        pos = [fx, fy]
        cv2.circle(img, (fx, fy), 80, (0, 0, 255), 2)
        cv2.putText(img, str(pos), (fx + 15, fy - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.line(img, (0, fy), (ws, fy), (0, 0, 0), 2)  # 수평선
        cv2.line(img, (fx, hs), (fx, 0), (0, 0, 0), 2)  # 수직선
        cv2.circle(img, (fx, fy), 15, (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "TARGET LOCKED", (ws - 350, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    else:
        center_x, center_y = ws // 2, hs // 2
        cv2.putText(img, "NO TARGET", (center_x - 110, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
        cv2.circle(img, (center_x, center_y), 80, (0, 0, 255), 2)
        cv2.circle(img, (center_x, center_y), 15, (0, 0, 255), cv2.FILLED)
        cv2.line(img, (0, center_y), (ws, center_y), (0, 0, 0), 2)  # x line
        cv2.line(img, (center_x, hs), (center_x, 0), (0, 0, 0), 2)  # y line

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # q를 누르면 루프에서 탈출
        break

cap.release()
cv2.destroyAllWindows()
