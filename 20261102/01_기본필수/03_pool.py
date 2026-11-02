"""실습 03 · 클래스 정의 없이 Sequential로 작은 CNN을 연결한다."""
import torch
from torch import nn

torch.manual_seed(42)
x = torch.rand(4, 3, 32, 32)
# MaxPool2d(2)는 2×2에서 최댓값을 선택한다. 기본 stride도 2이다.
# BEGIN B03
# TODO B03: 출력 높이·너비를 절반으로 만드는 MaxPool을 작성한다.
pool = nn.MaxPool2d(2) # 
# END B03
model = nn.Sequential(
    nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), pool,
    nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(32, 2),
) # nn.Conv2d(입력 채널 수, 커널(필터)의 개수, 커널(필터)의 크기, padding=1) -> 입력 채널 3개(RGB)를 받아, 3 X 3 크기의 커널(필터) 16개로 합성곱을 수행합니다.
  # padding이 1이므로 가로/세로 크기가 유지됩나다.(채널이 3에서 16으로 증가)
  # 비선형 활성화 함수인 ReLU()로 값의 크기나 차원을 바꾸지 않고, 텐서 내부의 음수값만 0으로 만듦니다.(차원 유지)
  # pool(nn.MaxPool2d()) 커널크기 2 스트라이드 2의 맥스 풀링을 적용하여 이미지의 가로와 세로 공간 크기를 절반(1/2)으로 축소합니다.(공간 크기 축소)
  # 입력 채널 16개를 받아 3 X 3 커널 32개로 두 번째 합성곱을 수행합니다. 패딩 1로 인해 가로/세로 크기는 유지됩니다.(채널이 16에서 32로 증가)
  # nn.ReLU() 활성화 함수를 한번 더 거칩니다.(차원 유지)
  # nn.MaxPool2d() 함수로 두번째 맥스 풀링을 거쳐 가로와 세로 크기가 다시 한번 절반(1/2)으로 줄어듭니다.(공간 크기 축소)
  # 적응형 평균 풀링입니다. nn.AdaptiveAvgPool2d(n) 함수로 입력 이미지의 크기가 얼마이든 상관없이, 추력되는 가로/세로 공간 크기를 강제로 n X n로 맞춰 채널별 평균 값을 계산합니다.(공간 크기가 1 X 1로 고정)
  # nn.Flatten() 함수로 1번째 차원(채널)부터 마지막 차원까지 일렬로 쭉 펼쳐주는 역할을 합니다.
  # 0번째 차원인 배치 크기(4)는 그대로 유지합니다.(2차원 벡터 형태로 평탄화: 32 X 1 X 1 = 32)
  # nn.Linear(특징 개수, 출력노드 개수) 함수로 32개의 Feature(특징)을 받아 최종 2개의 노드로 연결하는 선형 결합(Fully Connected Layer) 층입니다.
  # 보통 이진 분류나 2개 클래스의 Logits 값이 됩니다.(4, 2) -> 최종 출력 차원
for layer in model:
    x = layer(x)
    print(type(layer).__name__, tuple(x.shape))
