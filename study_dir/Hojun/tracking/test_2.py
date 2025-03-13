# 코드 실패



import numpy as np
import cv2
# Cascades 디렉토리의 haarcascade_frontalface_default.xml 파일을 Classifier로 사용
# faceCascade는 이미 학습 시켜놓은 XML 포멧이고, 이를 불러와서 변수에 저장함.
faceCascade = cv2.CascadeClassifier('D:\python\Cascade\haarcascade_frontalface_default.xml')

# 비디오의 setting을 준비함.
cap = cv2.VideoCapture(0) #0번이 내장카메라, 1번이 외장카메라
cap.set(3,1280) # set Width
cap.set(4,720) # set Height


while True:
    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    faces = faceCascade.detectMultiScale(
        gray, 
        scaleFactor=1.2,
  
        minNeighbors=3, 

        minSize=(20, 20)

    )
    for (x,y,w,h) in faces: 
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,255),2)

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

    cv2.imshow('video',img) 
    k = cv2.waitKey(1) & 0xff 

    if k == 27: 
        break
cap.release() #