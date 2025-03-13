import cv2
import os
from pyzbar.pyzbar import decode

def save_uid(data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'uid.txt')
    with open(file_path, "w") as file:
        file.write(data)
    print("UID 저장됨:", data)
    return True

class QRRecognizer:
    def __init__(self):
        # 카메라 캡처 객체 생성
        self.cap = cv2.VideoCapture(0)  # 기본 연결된 카메라 사용

        # 전체화면 창 설정
        cv2.namedWindow("QR 코드 스캐너", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("QR 코드 스캐너", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def run(self):
        try:
            while True:
                # 카메라로부터 이미지 읽기
                ret, frame = self.cap.read()
                if not ret:
                    continue  # 프레임을 제대로 못 읽었다면 다시 시도

                # QR 코드 인식
                decoded_objects = decode(frame)
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    print("Detected QR Code:", qr_data)
                    # QR 코드 주변에 사각형 그리기
                    points = obj.polygon
                    if len(points) > 4:
                        points = cv2.convexHull(points)
                    n = len(points)
                    for j in range(n):
                        cv2.line(frame, tuple(points[j]), tuple(points[(j + 1) % n]), (255, 0, 0), 3)

                    # UID 저장 후 종료
                    if save_uid(qr_data):
                        return  # 저장 성공 후 함수 종료

                # 결과 이미지 출력
                cv2.imshow("QR 코드 스캐너", frame)

                # 'q'를 누르면 반복문 탈출
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            # 자원 해제
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    qr_recognizer = QRRecognizer()
    qr_recognizer.run()
