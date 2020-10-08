import cv2 as cv
import numpy as np
from tensorflow.keras.models import load_model

# color -> gray 변환
img_color = cv.imread('my_num_1.jpg', cv.IMREAD_COLOR)
img_gray = cv.cvtColor(img_color, cv.COLOR_BGR2GRAY)

# 이미지 이진화를 통한 이미지 검출
ret, img_binary = cv.threshold(img_gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)


# 구조요소를 생성
kernel = cv.getStructuringElement( cv.MORPH_RECT, ( 5, 5 ) )
# cv2.getStructuringElement(커널의 형태, 커널의 크기, 고정점)
"""
커널의 형태는 직사각형(Rect), 십자가(Cross), 타원(Ellipse)이 있습니다.
커널의 크기는 구조 요소의 크기를 의미합니다. 이 때, 커널의 크기가 너무 작다면 커널의 형태는 영향을 받지 않습니다.
고정점은 커널의 중심 위치를 나타냅니다. 필수 매개변수가 아니며, 설정하지 않을 경우 사용되는 함수에서 값이 결정됩니다.

Tip : 고정점을 할당하지 않을 경우 조금 더 유동적인 커널이 됩니다
"""

# 모폴로지 연산
img_binary = cv.morphologyEx(img_binary, cv.MORPH_CLOSE, kernel)
# cv2.morphologyEx(원본 배열, 연산 방법, 구조 요소, 고정점, 반복 횟수, 테두리 외삽법, 테두리 색상)
"""
src? : 원본 배열
speckle? : 산재된 점의 형태
cv2.MORPH_DILATE	팽창 연산 : 밝은영역이 늘어나고 어두운 영역이 줄어듦
cv2.MORPH_ERODE 	침식 연산 : 밝은영역은 줄고 어두운 영역이 늘어남
cv2.MORPH_OPEN	    열림 연산 : 침식->팽창연산 수행, 스펙클(speckle)이 사라져 객체의 크기 감소를 원래대로 복구 가능해짐
cv2.MORPH_CLOSE	    닫힘 연산 : 팽창->침식연산 수행, 객체 내부의 홀(holes)이 사라져 크기 증가를 원래대로 복구 가능
cv2.MORPH_GRADIENT	그레이디언트 연산 :  팽창(src)-침식(src) 연산 수행, 객체의 가장자리가 반환
cv2.MORPH_TOPHAT	탑햇 연산 : src-열림, 스펙클이 사라지고 객체 크기가 보존된 결과
cv2.MORPH_BLACKHAT	블랙햇 연산 : src-닫힘, 어두운 영역이 채워져 사라졌던 홀 등이 표시됨
cv2.MORPH_HITMISS   히트미스 연산 : 모서리 검출하는데 활용
"""


# 이진화 완료된 전체 이미지 출력하고 키보드 입력 대기
cv.imshow('digit', img_binary)
cv.waitKey(0)

# 컨투어 검출
contours, hierarchy = cv.findContours(img_binary, cv.RETR_EXTERNAL, 
                        cv.CHAIN_APPROX_NONE) # cv.CHAIN_APPROX_SIMPLE 에서 NONE으로 변경해봄
    # contours, hierarchy = cv2.findContours(image, mode, method[, contours[, hierarchy[, offset]]]) : 모양분석 및 오브젝트 검출
    
""" contours    : 검출된 컴투어, list형으로 저장 오브젝트의 외곽선을 구성하는 x,y 좌표를 저장하고 있음
    hierarchy   : 검출된 검투어의 정보를 구조적으로 저장하고 (있음 list형)
    image       : 입력할 이미지, 바이너리 이미지로 바꿔서 입력해 줘야 함
    mode        : 검출된 엣지 정보를 계층 또는 리스트로 저장
    method      : 컨투어를 구성하는 포인트 검출 방법을 지정
    offset      : 지정한 크기만큼 컨투어를 구성하는 포인트 좌표를 이동하여 저장

    mode 속성
    1. cv.RETR_EXTERNAL : 가장 외부에 있는 컨투어만 검출
    2. cv.RETR_TREE     : 컨투어 내부에 다른 컨투어가 있을경우 계층구조를 만들어 줌
    3. cv.RETR_LIST     : 모든 컨투어가 같은 계층 레벨을 갖게됨.
    4. cv.RETR_CCOMP    : 모든 컨투어를 두개의 레벨 계층으로 재구성. 외부는 레벨1, 내부는 레벨2

    method 속성
    1. cv.CHAIN_APPROX_NONE : 모든 경계점을 저장
    2. cv.CHAIN_APPROX_SIMPLE : 선이 직선일 경우 시작점과 끝점만을 저장함
"""
for contour in contours:

    x, y, w, h = cv.boundingRect(contour)



    length = max(w, h) + 60
    img_digit = np.zeros((length, length, 1),np.uint8)

    new_x,new_y = x-(length - w)//2, y-(length - h)//2


    img_digit = img_binary[new_y:new_y+length, new_x:new_x+length]

    kernel = np.ones((5, 5), np.uint8)
    img_digit = cv.morphologyEx(img_digit, cv.MORPH_DILATE, kernel)

    cv.imshow('digit', img_digit)
    cv.waitKey(0)

    model = load_model('cnn_model.h5')

    img_digit = cv.resize(img_digit, (28, 28), interpolation=cv.INTER_AREA)

    img_digit = img_digit / 255.0

    img_input = img_digit.reshape(1, 28, 28, 1)
    predictions = model.predict(img_input)


    number = np.argmax(predictions)
    print(number)

    cv.rectangle(img_color, (x, y), (x+w, y+h), (255, 255, 0), 2)


    location = (x + int(w *0.5), y - 10)
    font = cv.FONT_HERSHEY_COMPLEX  
    fontScale = 1.2
    cv.putText(img_color, str(number), location, font, fontScale, (0,255,0), 2)
    

    cv.imshow('digit', img_digit)
    cv.waitKey(0)
    

cv.imshow('result', img_color)
cv.waitKey(0)
