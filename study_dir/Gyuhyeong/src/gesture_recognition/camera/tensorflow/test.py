import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
from collections import deque

# 모델 및 MediaPipe 설정
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
model = load_model('models/model.keras')

# 변수 설정
actions = ['next', 'prev']
seq_length = 20
seq = deque(maxlen=seq_length)
action_seq = deque(maxlen=3)  # 수정된 부분
fps = 30
cap = cv2.VideoCapture(0)

prev_x, prev_y = None, None
velocity_threshold = 0.5  # 속도 임계값 설정

while cap.isOpened():
    ret, img = cap.read()
    if not ret:
        continue

    img = cv2.flip(img, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for res in results.multi_hand_landmarks:
            # 손목의 landmark를 기준으로 속도 계산
            wrist = res.landmark[mp_hands.HandLandmark.WRIST]
            x, y = wrist.x, wrist.y

            if prev_x is not None and prev_y is not None:
                # 이전 프레임과의 거리 차이로 속도 계산
                velocity = np.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2) * fps  # 거리 차이에 fps를 곱하여 속도를 계산
                if velocity < velocity_threshold:
                    prev_x, prev_y = x, y
                    continue

            prev_x, prev_y = x, y

            joint = np.zeros((21, 4))
            for j, lm in enumerate(res.landmark):
                joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

            v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19], :3]
            v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :3]
            v = v2 - v1
            v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

            angle = np.arccos(np.clip(np.einsum('nt,nt->n', v[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18], :], v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]), -1.0, 1.0))
            angle = np.degrees(angle)

            d = np.concatenate([joint.flatten(), angle])
            seq.append(d)

            mp_drawing.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)

            if len(seq) == seq_length:
                input_data = np.expand_dims(np.array(seq), axis=0)
                y_pred = model.predict(input_data).squeeze()
                action = actions[np.argmax(y_pred)]
                action_seq.append(action)

                if len(action_seq) == action_seq.maxlen and action_seq.count(action_seq[0]) == action_seq.maxlen:
                    this_action = action_seq[0]
                    cv2.putText(img, f'{this_action.upper()}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
