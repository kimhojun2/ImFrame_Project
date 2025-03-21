import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

actions = ['next', 'prev', 'idle']
seq_length = 30

model = load_model('models/updated_model.keras')

# MediaPipe hands model 설정
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)
seq = []
current_action = None  # 현재 감지된 동작을 저장할 변수

while cap.isOpened():
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if result.multi_hand_landmarks:
        for res in result.multi_hand_landmarks:
            joint = np.zeros((21, 4))
            for j, lm in enumerate(res.landmark):
                joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

            v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19], :3]
            v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], :3]
            v = v2 - v1
            v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

            angle = np.arccos(np.clip(np.einsum('nt,nt->n', v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:]), -1.0, 1.0))
            angle = np.degrees(angle)

            d = np.concatenate([joint.flatten(), angle])
            seq.append(d)

            mp_drawing.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)

            if len(seq) == seq_length:
                input_data = np.expand_dims(np.array(seq, dtype=np.float32), axis=0)
                y_pred = model.predict(input_data).squeeze()
                i_pred = int(np.argmax(y_pred))
                conf = y_pred[i_pred]

                if conf >= 0.95:
                    current_action = actions[i_pred]  # 감지된 동작 업데이트
                seq = []  # 시퀀스 초기화

    if current_action:  # 감지된 동작이 있으면 계속 표시
        cv2.putText(img, f'{current_action.upper()}', org=(img.shape[1] // 2 - 50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=2)

    cv2.imshow('img', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
