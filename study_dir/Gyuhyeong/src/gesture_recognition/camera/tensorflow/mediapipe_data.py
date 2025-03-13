import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os

# MediaPipe hands model 설정
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# CSV 파일 로드
df = pd.read_csv('./slowfast/train.csv')

# 저장할 데이터셋 폴더 생성
os.makedirs('processed_dataset_4', exist_ok=True)

# 비디오 처리 함수
def process_video(video_path, label):
    cap = cv2.VideoCapture(video_path)
    data = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                joint = np.zeros((21, 4))
                for j, lm in enumerate(hand_landmarks.landmark):
                    joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

                # Compute angles between joints
                v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19], :3] # Parent joint
                v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], :3] # Child joint
                v = v2 - v1 # [20, 3]
                # Normalize v
                v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                # Get angle using arcos of dot product
                angle = np.arccos(np.einsum('nt,nt->n',
                    v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], 
                    v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:])) # [15,]

                angle = np.degrees(angle) # Convert radian to degree

                angle_label = np.array([angle], dtype=np.float32)
                angle_label = np.append(angle_label, label)


                d = np.concatenate([joint.flatten(), angle_label])
                data.append(d)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC 키를 누르면 종료
            break

    cap.release()
    return np.array(data)

# 각 비디오에 대한 처리
for _, row in df.iterrows():
    video_path = row['path']
    label = row['label']
    if label != 4:
        data = process_video(video_path, label)
        np.save(f'processed_dataset_4/data_{row["id"]}_{label}.npy', data)
        print(f'Processed {row["id"]} with label {label}, Data shape: {data.shape}')

print("All videos processed.")
