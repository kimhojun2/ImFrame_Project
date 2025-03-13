import cv2

# 웹캠 또는 비디오 파일 열기
cap = cv2.VideoCapture(0)  # 0은 웹캠을 의미함. 웹캠이 여러 개인 경우에는 1, 2, 3, ... 으로 변경 가능

while True:
    ret, frame = cap.read()  # 프레임 읽기
    if not ret:
        break

    # 이미지를 그레이스케일로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 불 꺼진 상태에서 불을 켤 때의 특징을 캡처하여 이후에 비교
    if 불_켜진_상태:
        # 불이 꺼진 것을 감지한 경우
        print("방에 불이 꺼졌습니다.")
        불_켜진_상태 = False
        # 여기에 원하는 동작 추가
    else:
        # 불이 켜진 것을 감지한 경우
        print("방에 불이 켜졌습니다.")
        불_켜진_상태 = True
        # 여기에 원하는 동작 추가

    # 화면에 프레임 출력
    cv2.imshow("Frame", frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료 시 해제
cap.release()
cv2.destroyAllWindows()
