"""Day14: 제공된 정상 이미지로 학습합니다. test는 읽지 않습니다."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch
from torch import nn
from torchvision.datasets import ImageFolder
from torchvision import transforms as tr
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

torch.set_num_threads(1)
torch.manual_seed(14)
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE

# 여기서는 [0,1] RGB 32×32로 학습한 교육용 source 가중치를 사용합니다.
# ImageNet ResNet18과 입력 변환을 섞지 않습니다.
transform = tr.Compose([tr.Resize((32, 32)), tr.ToTensor()])

# 손으로 읽는 지표 예제입니다. 모델의 실제 예측이라고 주장하지 않습니다.
y_true = [0] * 12 + [1] * 6 + [2] * 3
y_pred = [0] * 21
print("클래스 수:", [y_true.count(i) for i in range(3)]) # y_true((정답 데이터)[12, 6, 3])에 들어있는 0번, 1번, 2번 클래스의 수량입니다.
                                                        # 전체 21개 중 0번(circle)이 과반수 이상(57.1%)을 차지하고 있습니다.
print("Accuracy:", round(accuracy_score(y_true, y_pred), 4)) # 수식:(맞춘 샘플 수 / 전체 샘플 수 = 12 / 21 = approx 0.5714)
                                                             # 모델이 모든 문제를 0번으로 찍었을 때 0번 문제 12개는 맞췄지만 1번(6개), 2번(3개)은 다 틀렸습니다.
                                                             # 아무것도 학습하지 않고 한 번호로 찍었는데 정확도가 57.14%나 나오는 정확도의 한계를 잘 보여줍니다.
# TODO B04: f1_score에 average="macro", labels=[0,1,2], zero_division=0을 넣으세요.
# BEGIN B04
macro = f1_score(y_true, y_pred, average="macro", labels=[0, 1, 2], zero_division=0)  # f1_score 계산으로 바꾸세요.
                                                                                      # 클래스별 F1-score를 구한 뒤 이를 단순히 산술 평균한 값입니다.
                                                                                      # 0번(circle): Precision = (12 / 21 approx 0.571\), Recall = (12 / 12 = 1.0), F1 = 0.727
                                                                                      # 1번(square): Precision = 0 (예측 안 함), Recall = 0, F1 = 0.000
                                                                                      # 2번(triangle): Precision = 0 (예측 안 함), Recall = 0, F1 = 0.000
                                                                                      # Macro F1 평균: ((0.727 + 0.0 + 0.0) / 3 = approx 0.2424)
                                                                                      # wjdghkrehsms 57% 높게 보였지만, Macro F1은 0.2424로 매우 낮게 나옵니다.
                                                                                      # 이를 통해 모델이 소수 클래스(1, 2번)를 아예 못 맞추고 있다고 진단 할 수 있습니다.
# END B04
print("Macro F1:", round(macro, 4))
print(classification_report(y_true, y_pred, labels=[0, 1, 2], target_names=["circle", "square", "triangle"], zero_division=0, digits=3))
