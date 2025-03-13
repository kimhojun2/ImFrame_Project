import cv2
import torch
import numpy as np
from yolox.exp import get_exp
from yolox.utils import postprocess, vis
from yolox.data.data_augment import ValTransform

def main():
    # 모델 설정 및 가중치 로드
    exp = get_exp(exp_file=None, exp_name="yolox-nano")
    model = exp.get_model()
    model.eval()
    ckpt = torch.load("yolox_nano.pth", map_location="cpu")
    model.load_state_dict(ckpt["model"])
    model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    # 변환 설정
    val_transforms = ValTransform(legacy=False)

    # 웹캠 준비
    cap = cv2.VideoCapture(0)

    with torch.no_grad():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 이미지 전처리
            img, ratio = val_transforms(frame, None, exp.test_size)
            img = torch.from_numpy(img).unsqueeze(0)
            img = img.float()
            if torch.cuda.is_available():
                img = img.cuda()

            # 추론
            outputs = model(img)

            # 결과 포스트 프로세싱
            outputs = postprocess(outputs, num_classes=exp.num_classes, 
                                  conf_thre=exp.test_conf, nms_thre=exp.nmsthre)

            # 시각화
            if outputs[0] is not None:
                outputs = outputs[0].cpu()
                boxes = outputs[:, 0:4]
                scores = outputs[:, 4]
                cls_ids = outputs[:, 6].int()
                frame = vis(frame, boxes, scores, cls_ids, exp.class_names)

            # 화면에 표시
            cv2.imshow("YOLOX-Nano", frame)
            if cv2.waitKey(1) == 27:  # ESC 키를 누르면 종료
                break

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()