"""실습 04: 2 → 8 → 2 신경망의 순전파를 확인합니다."""
import torch
from torch import nn

torch.manual_seed(42) # 
# Sequential의 마지막 Linear를 수정해 출력 클래스 수가 2가 되게 하세요.
# 첫 Linear(2, 8)와 ReLU는 그대로 두세요. 모델 정의는 미리 제공했습니다.
# >>> B04
# TODO B04: 위 요구사항을 읽고 이 블록을 완성하세요.
model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2)) # nn.Linear() 함수에 2개의 입력 특징을 받아 8개의 노드로 확장하는 은닉층(Hidden Layer)입니다.
                                                                   # 활성화 함수 nn.ReLU()로 노드를 거친 값 중 음수는 0으로 자르고 양수만 그대로 통과시켜 신경망에 '비선형성'이라는 유연함을 부여합니다.
                                                                   # nn.Linear() 함수에 8개의 신호를 받아 최종적으로 2개의 클래스(또는 수치)로 압축하여 내보내는 출력층(Output Layer)입니다.
# <<< B04
X = torch.tensor([[1.0, 2.0], [3.0, 4.0], [0.0, 1.0], [2.0, 0.0]])
logits = model(X) # 입력 X는 4행 2열(4개의 데이터 샘플, 각2개이 특징)의 형태입니다.
                  # 이 데이터가 모델을 통과하며 수학적 행렬 곱셈을 거치며 (4, 2) * Linear(2, 8) -> (4, 8) * Linear(8, 2) -> (4, 2)로 변화합니다.
                  # 최종 예층 점수 logits에 4행 2열의 구조가 남게 됩니다.
print("입력:", tuple(X.shape))
print("출력:", tuple(logits.shape))
print("파라미터 수:", sum(p.numel() for p in model.parameters())) # p.numel()은 각 레이어의 가중치(Weight)와 편향(Bias) 텐서 안에 들어있는 실제 숫자(원소)의 총 개수를 세어주는 함수입니다.
                                                                # 첫번째 Linear 층: 가중치(2 * 8 = 16) + bias(8) = 24개
                                                                # 두번째 Linear 층: 가중치(8 * 2 = 16) + bias(2) = 18개
                                                                # 총합: 24 + 18 = 42
# logits는 원시 점수입니다. 이 시점에는 학습하지 않았습니다.
