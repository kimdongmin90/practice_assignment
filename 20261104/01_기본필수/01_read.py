from pathlib import Path
import os
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent) # 01_read.py(현재 파이썬 파일)이 위치한 실제 폴더 경로를 찾아서 그곳으로 작업 디렉토리를 변경합니다.
                                          # 같은 폴더에 있는 scene.png를 바로 불러올 수 있습니다.

# 색상 이미지: 한 픽셀의 값 순서는 B, G, R입니다.
# >>> TODO B01
# scene.png를 cv2.imread로 읽어 image에 저장하세요. flags를 생략하면 BGR 컬러로 읽습니다.
image = cv2.imread("scene.png") # scene.png 파일의 이미지를 읽어와 Numpy 행렬(array) 형태로 image 변수에 저장합니다.
# <<< TODO B01
print("shape:", image.shape) # 이미지의 (세로 픽셀 수, 가로 픽셀 수, 채널 수)를 출력합니다. 
                             # 마지막 숫자가 3인 것은 이 이미지가 컬러이미지(BGR)임을 뜻합니다.
                             # 예상 출력: shape: (480, 640, 3)
print("dtype:", image.dtype) # 이미지 데이터 타입을 출력합니다.
                             # 일반적인 이미지는 색상당 0~255 단계를 표현하는 uint8(8비트 부호 없는 정수) 타입을 가집니다.
                             # 예상 출력: dtype: unit8
print("min/max:", int(image.min()), int(image.max())) # 이미지 전체에서 가장 어두운 픽셀 값(최솟값)과 가장 밝은 픽셀 값(최대값)을 찾아 정수로 출력합니다.
                                                      # 예상 출력: min/max: 0.255
print("빨강 패치의 BGR:", image[30, 30].tolist()) # 이미지의 세로 30번째, 가로 30번째 좌표에 있는 픽셀의 색상 값을 리스트로 변환하여 출력합니다.
                                                # OpenCV는 BGR 순서이므로, 빨간색 부위라면 [B, G, R] 중 세 번째 R값이 높게 나옵니다.
                                                # 예상 출력: 빨강 패치의 BGR [0, 0, 255](완전한 빨간색일 경우)
saved = cv2.imwrite("p01_copy.png", image) # 메모리에 로드된 image 데이터를 현재 폴더에 p01_copy.png라는 이름의 파일로 복사본을 저장합니다.
                                           # 성공하면 True, 실패하면 False를 반환합니다.
print("PNG 저장:", saved)
