import cv2
import numpy as np #importing libraries
cap = cv2.VideoCapture(-1)
while 1: 
    ret,img = cap.read() #reading the frames
    if ret == False:
        break;
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 
    blur = cv2.GaussianBlur(gray,(5,5),0) 
    ret,thresh1 = cv2.threshold(blur,70,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    cv2.imshow('input',img) #disPlaying the frames
    k=cv2.waitKey(10)
    if k == 27:
        break
