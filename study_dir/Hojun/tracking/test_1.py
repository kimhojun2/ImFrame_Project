# 사용 실패 
# 객체 탐지를 이상하게 함

import cv2
import torch
import numpy as np
from YOLOX.yolox.exp import get_exp
from YOLOX.yolox.utils import postprocess, vis

def main():
    # 모델과 실험 설정 로드
    exp = get_exp(exp_name="yolox-nano")
    model = exp.get_model()
    model.eval()

    # CUDA 사용 가능 여부에 따라 디바이스 설정
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # 웹캠 준비
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    with torch.no_grad():
        while True:
            # 웹캠으로부터 이미지 캡처
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            # 이미지 전처리
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (exp.test_size[0], exp.test_size[1]))
            img = img.astype(np.float32) / 255.0
            img = np.transpose(img, (2, 0, 1))
            img = torch.from_numpy(img)
            img = img.unsqueeze(0).to(device)

            # 모델 추론
            outputs = model(img)

            # 후처리 및 시각화 준비
            outputs = postprocess(outputs, num_classes=exp.num_classes, 
                                  conf_thre=exp.test_conf, nms_thre=exp.nmsthre)
            
            # 클래스 ID 추출
            if outputs[0] is not None:
                outputs = outputs[0].cpu()
                cls_ids = outputs[:, 6].int().tolist()
            else:
                cls_ids = []

            # 시각화
            frame = vis(frame, outputs, cls_ids)

            # 결과 출력
            cv2.imshow('YOLOX Object Detection', frame)

            # 'q' 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

