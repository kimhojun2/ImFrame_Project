#!/usr/bin/env python3
# 이 스크립트는 NVIDIA CORPORATION의 저작권을 갖고 있으며, 상업적으로 자유롭게 사용, 수정, 배포할 수 있도록 허가되어 있습니다.

import argparse
import datetime
import math
import sys
import os

from jetson_inference import detectNet
from jetson_utils import (videoSource, videoOutput, saveImage, Log,
                          cudaAllocMapped, cudaCrop, cudaDeviceSynchronize)

# 커맨드 라인 인자를 파싱하기 위한 설정
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=detectNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

# 입력 스트림, 출력 스트림, 네트워크 모델, 오버레이 설정 등의 인자를 정의
parser.add_argument("input", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 
parser.add_argument("--snapshots", type=str, default="images/test/detections", help="output directory of detection snapshots")
parser.add_argument("--timestamp", type=str, default="%Y%m%d-%H%M%S-%f", help="timestamp format used in snapshot filenames")

# 인자들을 파싱하고 에러가 있는 경우 도움말을 출력 후 종료
try:
    args = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

# 스냅샷을 저장할 디렉토리가 존재하는지 확인하고 없으면 생성
os.makedirs(args.snapshots, exist_ok=True)

# 비디오 출력 객체 생성
output = videoOutput(args.output, argv=sys.argv)
	
# 객체 감지 네트워크 로드
net = detectNet(args.network, sys.argv, args.threshold)

# 비디오 소스 생성
input = videoSource(args.input, argv=sys.argv)

# EOS(End of Stream) 또는 사용자 종료 시까지 프레임 처리
while True:
    # 다음 이미지 캡처
    img = input.Capture()

    if img is None: # 타임아웃 발생 시 계속
        continue  

    # 이미지에서 객체 감지 (오버레이와 함께)
    detections = net.Detect(img, overlay=args.overlay)

    # 감지된 객체의 수 출력
    print("detected {:d} objects in image".format(len(detections)))

    timestamp = datetime.datetime.now().strftime(args.timestamp)

    # 각 감지된 객체에 대해
    for idx, detection in enumerate(detections):
        print(detection)
        roi = (int(detection.Left), int(detection.Top), int(detection.Right), int(detection.Bottom))
        snapshot = cudaAllocMapped(width=roi[2]-roi[0], height=roi[3]-roi[1], format=img.format)
        cudaCrop(img, snapshot, roi)
        cudaDeviceSynchronize()
        saveImage(os.path.join(args.snapshots, f"{timestamp}-{idx}.jpg"), snapshot)
        del snapshot

    # 이미지 렌더링
    output.Render(img)

    # 상태바 업데이트
    output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))

    # 성능 정보 출력
    net.PrintProfilerTimes()

    # 입력/출력 스트림이 종료되면 반복 중단
    if not input.IsStreaming() or not output.IsStreaming():
        break
