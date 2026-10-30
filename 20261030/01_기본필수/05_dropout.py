import torch
from torch import nn

torch.manual_seed(42)
X = torch.ones(2, 4) # 모든 원소의 값이 1.0으로 가득 찬 2행 4열짜리 텐서 격자를 torch.ones() 함수로 만듦니다.
dropout = nn.Dropout(p=0.5) # p(%) 확률로 데이터를 0올 만들어 버리는 필터를 nn.Dropout() 함수로 사용합니다.
dropout.train()
for i in range(3):
    print("train", i + 1, dropout(X).tolist()) # 인공지능에게 학습을 선언하고 데이터를 통과시킵니다.
                                               # 3번 반복하는 동안 매번 실행 시 랜덤하게 다른 위치의 원소들이 0으로 지워집니다.
                                               # 절반을 지우면 전체 데이터의 합(에너지)가 반토막이 납니다. 이를 막기 위해 파이토치는 살아남은 숫자에 일부러(1 / (1 - p) -> 여기서는 1 /(1 - 0.5) = 2)를 곱해주는 보정 연산을 수행합니다.
                                               # 1.0 이었던 숫자 중 살아남은 값은 2.0이 되고, 죽은 값은 0.0이 됩니다.
                                               # 매 줄마다 무작위로 위치가 바뀝니다.
# Dropout을 평가 모드로 바꾸세요. dropout.eval()은 mode만 바꿉니다.
# 평가 모드의 Dropout은 입력을 그대로 전달하며, gradient 비활성화와는 별개의 기능입니다.
# >>> B06
# TODO B06: 위 요구사항에 맞게 이 블록만 완성합니다.
dropout.eval() # [dropout.train(shuffle = False)로 작성하는 것은 지양한다.
# <<< B06
for i in range(3):
    print("eval", i + 1, dropout(X).tolist()) # 인공지능에게 평가한다고 선언하는 상태입니다.
                                              # 평가 모드에서는 드롭아웃 기능이 OFF됩니다.
                                              # 단 하나의 숫자도 0으로 지워지지 않고, 어떤 값의 변형도 없이 원래 입력했던 1.0 배열이 3번 모두 똑같이 출력됩니다.
