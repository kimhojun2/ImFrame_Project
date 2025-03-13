import cv2
import timeit

# 웹캠 영상에서 객체를 검출하는 함수
def videoDetector(cascade):
    # 웹캠 열기
    cam = cv2.VideoCapture(0)

    while True:
        start_t = timeit.default_timer()  # 알고리즘 시작 시간 기록

        ret, img = cam.read()  # 웹캠으로부터 영상 프레임 읽기
        if not ret:
            break

        # 영상 크기 조정
        img = cv2.resize(img, dsize=None, fx=1.0, fy=1.0)
        # 그레이 스케일 변환qq
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cascade 얼굴 탐지 알고리즘 적용
        results = cascade.detectMultiScale(gray,
                                            scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(20, 20))

        # 검출된 객체 주변에 사각형 그리기
        for box in results:
            x, y, w, h = box
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), thickness=2)

        terminate_t = timeit.default_timer()  # 알고리즘 종료 시간 기록
        FPS = 'fps' + str(int(1./(terminate_t - start_t)))  # FPS 계산
        cv2.putText(img, FPS, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

        # 영상 출력
        cv2.imshow('facenet', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()  # 웹캠 해제
    cv2.destroyAllWindows()

# 가중치 파일 경로
cascade_filename = 'haarcascade_frontalface_alt.xml'
# 모델 불러오기
cascade = cv2.CascadeClassifier(cascade_filename)

# 웹캠에서 객체 검출 실행
videoDetector(cascade)