import torch
from torch import nn

torch.manual_seed(42)
X = torch.tensor([[1.,2.],[2.,1.],[3.,4.],[4.,3.]]) # torch.tensor(...) 함수로 4행 2열짜리 실수형 입력 데이터 셋을 준비합니다.
bn = nn.BatchNorm1d(num_features=8)
model = nn.Sequential(nn.Linear(2, 8), bn, nn.ReLU()) # nn.Linear() 함수로 2개의 입력값을 받아 8개 조합된 신호로 확장하여 내보내는 첫번째 층 입니다.
                                                      # Linear를 통해 나온 num_features(8개) 신호가 너무 튀지 않도록 평균은 0, 분산은 1이 되도록 nn.BatchNorm1d() 함수(데이터 고속 정렬 필터)로 다듬어줍니다.
model.train() # 배치 정규화는 드롭아웃처럼 학습할 때와 평가할 때 행동이 다릅니다.
              # 이 명령을 통해 지금은 학습 중이니 매 배치 데이터의 평균과 분산을 실시간 계산해 저장하라고 합니다.
# model에 X를 넣어 output을 구하세요. 입력 (4,2)는 Linear에서 (4,8)이 됩니다.
# BatchNorm1d(8)은 8개 특성의 통계를 유지합니다.
# >>> B07
# TODO B07: 위 요구사항에 맞게 이 블록만 완성합니다.
output = model(X) # 4행 2열 데이터가 모델을 통과하며 Linear를 거쳐 4행 8열로  바뀌고, BatchNorm1d에 의해 8개 열 단위로 정규화(평균 0, 분산 1 변환)된 후 ReLU 필터를 거쳐 최종 output으로 안착합니다.
# <<< B07
print("입력:", tuple(X.shape), "출력:", tuple(output.shape))
print("running_mean:", tuple(bn.running_mean.shape))
before = bn.running_mean.clone()
model.eval()
with torch.no_grad():
    model(X)
print("eval에서 통계 유지:", torch.equal(before, bn.running_mean))
