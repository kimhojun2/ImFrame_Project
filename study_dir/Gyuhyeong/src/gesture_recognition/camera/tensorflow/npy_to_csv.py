import numpy as np
import csv
import os

actions = ['next', 'prev', 'idle']
data_dir = 'dataset'
output_file = 'landmarks.csv'

# CSV 파일에 헤더 준비
header = ["label"]
for i in range(1, 22):  # 21 landmarks
    header.extend([f'landmark{i}_x', f'landmark{i}_y', f'landmark{i}_z', f'landmark{i}_visibility'])

header.extend(['angle' + str(i) for i in range(1, 16)])  # 추가된 각도 정보

# CSV 파일 열기 및 헤더 작성
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)

    # 각 액션에 대한 .npy 파일 읽기
    for action in actions:
        action_folder = os.path.join(data_dir, action)
        if not os.path.exists(action_folder):
            continue

        # 폴더 내의 모든 .npy 파일에 대해 처리
        for filename in os.listdir(action_folder):
            if filename.endswith('.npy'):
                file_path = os.path.join(action_folder, filename)
                data = np.load(file_path)  # 데이터 로드

                # 각 데이터 프레임 처리
                for frame_data in data:
                    # 레이블과 랜드마크 데이터 추출
                    frame = [action]
                    landmarks = frame_data[:, :-1].flatten()  # 좌표와 가시성 펼치기
                    angles = frame_data[:, -1]  # 마지막 열은 각도 데이터
                    frame.extend(landmarks)
                    frame.extend(angles)
                    writer.writerow(frame)  # CSV에 작성

print(f'Data written to {output_file}')
