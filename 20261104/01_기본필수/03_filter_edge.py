from pathlib import Path
import os
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)

image = cv2.imread("noisy.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# >>> TODO B03
# gray를 (5,5), sigmaX=0으로 흐리게 하여 blur를 만드세요. blur에 Canny 80,160을 적용하여 edge를 만드세요.
blur = cv2.GaussianBlur(gray, (5, 5), sigmaX=0) # gray 명령어로 원본 그레이스케일 이미지를 블러로 적용합니다.
                                                # 가우시안 커널의 (가로 크기, 세로 크기)를 적용하며 크기가 커질수록 이미지가 더 많이 흐려집니다.(반드시 홀수로 지정)
                                                # X방향(가로)의 표준편차를 sigmaX= 명령어로 지정합니다.
                                                # 0으로 지정하면 OpenCV가 지정된 커널 크기(5,5)에 맞춰 자동으로 가장 적절한 표준편차 값을 계산하여 적용합니다.
edge = cv2.Canny(blur, 80, 160, apertureSize=3, L2gradient=False) # 노이즈가 제거된 블러 이미지를 입력으로 넣습니다.(노이즈가 먼저 제거되어야 깔끔한 경계선이 나옵니다.)
                                                                  # 에지인지 아닌지 모호한 경계선 중에 이 값보다 낮으면 무조건 에지가 아니라고 판단할 하한 임계값(80)을 설정하고 이 값보다 낮으면 아니라고 판단하면 제거합니다.
                                                                  # 픽셀 값의 변화량이 이 값보다 크면 100% 확실한에지로 판단할 상한 임계값(160)을 설정합니다.
                                                                  # 변화량이 80 ~ 160에 있는 애매한 선들은 160 이상의 확실한 에지와 연결되어 있을 때만 최종 에지로 인정됩니다.
# <<< TODO B03
cv2.imwrite("p03_blur.png", blur)
cv2.imwrite("p03_edge.png", edge)
print("설정: Gaussian (5,5), sigmaX=0, Canny 80/160")
print("Shape:", blur.shape, edge.shape)
print("Edge 픽셀:", int(np.count_nonzero(edge)))
