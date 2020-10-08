#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tensorflow as tf
import cv2
import numpy as np
import math
from tensorflow.keras.models import load_model

def process(img_input):

    gray = cv2.cvtColor(img_input, cv2.COLOR_BGR2GRAY) # 색을 칼라에서 그레이로 바꿔준다.
    gray = cv2.resize(gray, (28, 28), interpolation = cv2.INTER_AREA) # cv2.resize(원본 이미지, 결과 이미지 크기, 보간법)
    
    """   
    cv2.resize 보간법 옵션 
    cv2.INTER_NEAREST	    이웃 보간법
    cv2.INTER_LINEAR	    쌍 선형 보간법      -> 이미지를 확대, 가장 많이 쓰임
    cv2.INTER_LINEAR_EXACT	비트 쌍 선형 보간법
    cv2.INTER_CUBIC	        바이큐빅 보간법     -> 이미지 확대
    cv2.INTER_AREA	        영역 보간법         -> 이미지 축소
    cv2.INTER_LANCZOS4	    Lanczos 보간법
    """

    (thresh, img_binary) = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)


    h,w = img_binary.shape

  
    ratio = 100/h
    new_h = 100
    new_w = w * ratio

    img_empty = np.zeros((110,110), dtype=img_binary.dtype)
    img_binary = cv2.resize(img_binary, (int(new_w), int(new_h)), interpolation=cv2.INTER_AREA)
    img_empty[:img_binary.shape[0], :img_binary.shape[1]] = img_binary

    img_binary = img_empty


    cnts = cv2.findContours(img_binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours, hierarchy = cv2.findContours(image, mode, method[, contours[, hierarchy[, offset]]]) : 모양분석 및 오브젝트 검출
    """
    contours    : 검출된 컴투어, list형으로 저장 오브젝트의 외곽선을 구성하는 x,y 좌표를 저장하고 있음
    hierarchy   : 검출된 검투어의 정보를 구조적으로 저장하고 (있음 list형)
    image       : 입력 이미지 바이너리 이미지로 바꿔서 입력해 줘야 함
    mode        : 검출된 엣지 정보를 계층 또는 리스트로 저장
    method      : 컨투어를 구성하는 포인트 검출 방법을 지정
    offset      : 지정한 크기만큼 컨투어를 구성하는 포인트 좌표를 이동하여 저장
    """

    """
    mode 속성
    1. cv2.RETR_EXTERNAL : 가장 외부에 있는 컨투어만 검출
    2. cv2.RETR_TREE     : 컨투어 내부에 다른 컨투어가 있을경우 계층구조를 만들어 줌
    3. cv2.RETR_LIST     : 모든 컨투어가 같은 계층 레벨을 갖게됨.
    4. cv2.RETR_CCOMP    : 모든 컨투어를 두개의 레벨 계층으로 재구성. 외부는 레벨1, 내부는 레벨2

    method 속성
    1. cv2.CHAIN_APPROX_NONE : 모든 경계점을 저장
    2. cv2.CHAIN_APPROX_SIMPLE : 선이 직선일 경우 시작점과 끝점만을 저장함
    """

    # 컨투어의 무게중심 좌표를 구함. 
    M = cv2.moments(cnts[0][0]) # 윤곽선에서 모멘트를 계산, cv2.moment(배열, 이진화 이미지)
    center_x = (M["m10"] / M["m00"])
    center_y = (M["m01"] / M["m00"])

    # 무게 중심이 이미지 중심으로 오도록 이동시킴. 
    height,width = img_binary.shape[:2]
    shiftx = width/2-center_x
    shifty = height/2-center_y

    Translation_Matrix = np.float32([[1, 0, shiftx],[0, 1, shifty]])
    img_binary = cv2.warpAffine(img_binary, Translation_Matrix, (width,height))
    # 이미지 이동 cv2.warpAffine(img, M, (w,h)) : w,h를 shiftx, shifty 픽셀만큼 이동함.

    img_binary = cv2.resize(img_binary, (28, 28), interpolation=cv2.INTER_AREA)
    val_flatten = img_binary.flatten() / 255.0

    return val_flatten


cap = cv2.VideoCapture(1) # VideoCapture() 0은 웹캠이 하나, 1,2 일경우 웹캡이 두개 이상이어서 어느카메라를 쓸지 인덱스로 지정해주는 것임
                          # 만일 VideoCapture('이미지경로') 로 하면 이미지를 불러옴
# if cap.isOpen(): 
    # cap.get(?)은 cap(cv2.VideoCapture())의 속성을 반환함
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # cv2.CAP_PROP_FRAME_WIDTH는 프레임의 너비
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # cv2.CAP_PROP_FRAME_HEIGHT는 프레임의 높이

model = load_model('./12-0.0579.hdf5', compile = False)  

while 1:

    ret, img_color = cap.read()

    if ret == False:
        break;

    img_input = img_color.copy()
    cv2.rectangle(img_color, (250, 150),  (width-250, height-150), (0, 0, 255), 3)
    cv2.imshow('bgr', img_color)

    img_roi = img_input[150:height-150, 250:width-250]


    key = cv2.waitKey(1)

    if key == 27:
        break
    elif key == 32:
        flatten = process(img_roi)
        
        predictions = model.predict(flatten[np.newaxis,:])

        with tf.compat.v1.Session() as sess:
            print(tf.argmax(predictions, 1).eval())

        cv2.imshow('img_roi', img_roi)
        cv2.waitKey(0)


cap.release()
cv2.destroyAllWindows()


cap.release()
cv2.destroyAllWindows()


# In[ ]:




