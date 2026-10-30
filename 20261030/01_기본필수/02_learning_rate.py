from pathlib import Path
import pandas as pd
import torch
from torch import nn

torch.set_num_threads(1)
base = Path(__file__).resolve().parent
df = pd.read_csv(base / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long)
# test 4건은 읽은 표에만 있으며 학습/평가 Tensor로 만들지 않습니다.

# 학습률 후보 두 개를 리스트로 쓰세요: 0.001, 0.01.
# 모델·seed·20 epochs·AdamW·weight_decay=0은 그대로 둡니다.
# >>> B03
# TODO B03: 위 요구사항에 맞게 이 블록만 완성합니다.
learning_rates = [0.01] # 학습률을 0.01로 설정합니다
# <<< B03
loss_fn = nn.CrossEntropyLoss() # 다지선다 문제 전용 표준 채점기 nn.CrossEntropyLoss() 함수로 loss_fn에 상시 대기시켜둡니다.
for lr in learning_rates: # 만약 리스트에 [0.01, 0.001] 등 여러 보폭이 들어있다면, 하나씩 꺼내어 독립적인 인공지능 학습 실험을 릴레이로 수행하게 만드는 반복문(실험대)입니다.
    torch.manual_seed(42) # torch.manual_seed() 함수는 반드시 for문 안쪽에 위치해야 하며, 그래야 다음 보폭(lr) 실험으로 넘어갔을 때 인공지능 뇌 세포 가중치 상태가 처음 상태(42) 세팅으로 리셋되어 공정한 대조 실험이 성립됩니다.
    model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2)) # nn.Sequential(...) 함수를 통해 앞선 단계와 동리하게 "2개 입력 -> 8개 생각 -> ReLU 필터 -> 2개 출력" 구조의 인공지능뇌 구조를 매 실험마다 새것으로 조합합니다. 
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0) # 현업 딥러닝(대형 언어 모델 등)에서 가장 성능이 좋아 널리 쓰이는 최적화 알고리즘인 torch.optim.AdamW(...) 함수를 이용합니다.
                                                                               # 가중치가 너무 과도하게 커지는 것을 막아주는 규제 법칙인 weight_decay(가중치 감쇠) 옵션은 0.0으로 꺼두어 순수 보폭(lr)의 영향력만 관찰합니다.
    losses = [] # 이번 학습률 보폭으로 진행시, 각 회차(epoch)마다 튀어나올 오차 점수들을 순서대로 저장할 장소를 개설합니다.
    for epoch in range(20):
        model.train()
        optimizer.zero_grad()
        loss_fn(model(X_train), y_train).backward()
        optimizer.step()
        # 갱신이 끝난 모델의 valid loss를 기록합니다. valid로 backward하지 않습니다.
        model.eval()
        with torch.no_grad():
            losses.append(loss_fn(model(X_valid), y_valid).item())
    print("lr:", lr, "처음 5개:", [round(x, 6) for x in losses[:5]])
    print("마지막 valid loss:", round(losses[-1], 6))
