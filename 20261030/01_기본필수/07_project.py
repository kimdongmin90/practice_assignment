from pathlib import Path
import pandas as pd
import torch
from torch import nn

torch.set_num_threads(1)
base = Path(__file__).resolve().parent
import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 PNG에 저장합니다.
import matplotlib.pyplot as plt
df = pd.read_csv(base / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long)
# test 4건은 읽은 표에만 있으며 학습/평가 Tensor로 만들지 않습니다.

# 실습 07~08: 기준 lr과 비교 lr만 다릅니다. 더 나쁘게 나와도 그대로 보고합니다.
loss_fn = nn.CrossEntropyLoss()
summary = [] # baseline 실험이 끝난 기록과 candidate 실험이 끝난 기록을 마지막에 모아 통합 성적표를 만듦니다.
for name, lr in [("baseline", 0.001), ("candidate", 0.01)]: # 1회차 name은 "baseline", lr은 0.001이 되어 안쪽 코드가 돌아갑니다.
                                                            # 2회차 name은 "candidate", lr은 0.01이 되어 처음부터 다시 리셋되어 돌아갑니다.
    torch.manual_seed(42)
    model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0)
    history = []
    for epoch in range(1, 21):
        model.train()
        optimizer.zero_grad()
        loss = loss_fn(model(X_train), y_train)
        # 이미 zero_grad와 loss 계산이 끝났습니다. loss.backward() 다음 optimizer.step()을 호출하세요.
        # 학습 데이터만 사용합니다. 비교 후보마다 모델을 처음부터 새로 만듭니다.
        # >>> B08
        # TODO B08: 위 요구사항에 맞게 이 블록만 완성합니다.
        loss.backward()
        optimizer.step()
        # <<< B08
        model.eval()
        with torch.no_grad():
            train_loss = loss_fn(model(X_train), y_train).item() # 20바퀴의 실시간 중간 채점 구역 -> 이번 epoch에서 수정된 인공지능에게 학습을 시켜보며 loss 값을 뽑아냅니다.
            valid_loss = loss_fn(model(X_valid), y_valid).item() # 20바퀴의 실시간 중간 채점 구역 -> 동일한 상태의 인공지능에게 평가를 시켜보며 실전 loss 오차값을 뽑아냅니다.
        # 한 epoch의 번호와 갱신 후 train_loss, valid_loss를 기록하세요.
        # history.append([epoch, train_loss, valid_loss]) 형태로 추가합니다.
        # >>> B09
        # TODO B09: 위 요구사항에 맞게 이 블록만 완성합니다.
        history.append([epoch, train_loss, valid_loss]) # 현재 epoch, 학습 loss값, 평가 loss값 3가지 핵심 정보를 하나의 세트로 묶어 history에 한 줄씩 추가합니다.
        # <<< B09
    table = pd.DataFrame(history, columns=["epoch", "train_loss_eval", "valid_loss"]) # history를 pd.DataFrame() 함수로 가독성 좋은 판다스 데이터프레임(표) 구조로 바꿉니다.
    table.to_csv(base / f"history_{name}.csv", index=False) # 이번 실험의 name을 붙여 history_baseline.csv로 저장합니다.
    best = table.loc[table["valid_loss"].idxmin()] # valid_loss가 가장 작았던 최적의 행의 번호를 idxmin() 함수로 찾아 내용을 가져옵니다.
    summary.append([name, lr, int(best["epoch"]), best["valid_loss"]]) # summary.append() 함수로 [실험이름, 학습률, 베스트에포크, 최저오차] 세트를 추가합니다.
    plt.figure(figsize=(8, 5)) # figsize=(가로, 세로) 함수로 크기를 지정하고 plt.figure() 함수로 그래프를 그립니다.
    plt.plot(table["epoch"], table["train_loss_eval"], label="train (eval mode)") # x축은 epoch, y축은 train_loss_eval 값으로 지정하고 label="선 이름(train(eval mode))" 옵션 추가 후 plt.plot(x축, y축) 함수로 꺾은선 그래프를 그립니다.
    plt.plot(table["epoch"], table["valid_loss"], label="valid") # x축은 epoch, y축은 valid_loss 값으로 지정하고 label="선 이름(valid)" 옵션 추가 후 plt.plot(x축, y축) 함수로 꺾은선 그래프를 그립니다.
    plt.axvline(best["epoch"], linestyle="--", label="best epoch") # plt.axvline( , 스타일, 이름) 함수로 best["epoch"] 위치에 linestyle="--(세로 점선)" 명령어로 선 스타일, label="" 명령어로 이름 옵션을 지정하여 표시합니다.
    plt.xlabel("Epoch") # plt.xlabel("이름") 함수로 그래프 x(가로)축 맨 아래 Epoch(이름)를 추가합니다.
    plt.ylabel("Loss") # plt.ylabel("이름") 함수로 그래프 y(세로)축 왼쪽 옆에 Loss(이름)를 추가합니다.
    plt.legend() # plt.legend() 함수로 구석에 각 선들이 무엇을 뜻하는지 알려주는 범례(이름표 모음 상자)를 띄웁니다.
    plt.tight_layout() # plt.tight_layout() 함수로 그래프 안의 글자나 축이 경계선 밖으로 깨져나가지 않도록 정렬 양식을 자동 조절합니다.
    plt.savefig(base / f"curves_{name}.png", dpi=150) # plt.savefig(base / "파일이름.확장자", 해상도) 함수로 f"curves_{name}.png"("파일이름.확장자"), dpi= 명령어로 해상도 옵션을 지정해서 표시합니다.
    plt.close() # plt.close() 함수로 그래프 그리는 것을 닫습니다.
result = pd.DataFrame(summary, columns=["setting", "lr", "best_epoch", "best_valid_loss"]) # 여러 실험군의 핵심 요약 데이터가 쌓인 summary를 모아 최종 비교 테이블을 만듦니다.
result.to_csv(base / "experiment_table.csv", index=False) # result.to_csv() 함수로 최종 비교 테이블을 "experiment_table.csv"라는 종합 엑셀 파일로 저장합니다.
print(result.round(6).to_string(index=False)) # round() 함수로 긴 소수점 수치를 반올림하여 정리하고, index(지저분한 행 번호)를 뗀 후 콘솔창에 출력합니다.
print("test 미사용 / best epoch는 관찰한 최소 지점, 기본필수에서는 모델 저장·복원하지 않음") # 이번 인공지능 실험 조건의 특이사항을 마지막으로 알려주며 마감합니다.
