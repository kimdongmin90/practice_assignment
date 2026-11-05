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
import cv2
train = ImageFolder(DATA / "train", transform=transform)
valid = ImageFolder(DATA / "valid", transform=transform)
X_train = torch.stack([train[i][0] for i in range(len(train))]) # 리스트 컴프리헨션을 사용하여 train 데이터셋의 모든 인덱스를 순회합니다.
                                                                # train[i]는 (이미지 텐서, 정답 인덱스) 형식의 튜플을 반환하므로 [0]을 통해 이미지 텐서만 골라냅니다.
                                                                # 차원 변화: 개별 이미지는 (3, 32, 32) 크기를 가집니다.
                                                                # 학습 데이터셋의 총 개수를 \(N_{train}\)이라고 할 때, torch.stack은 새로운 차원(0번째 축)을 만들어 이들을 위로 쌓아 올립니다.
                                                                # 결과적으로 X_train은 (N_train, 3, 32, 32)라는 완벽한 4차원 미니배치 형태의 텐서가 됩니다.
y_train = torch.tensor(train.targets, dtype=torch.long) # train.targets에는 각 이미지의 정답지 리스트가 들어있습니다.
                                                        # 이를 PyTorch 연산이 가능한 정수형 텐서로 변환합니다.
                                                        # X_train의 0번째 차원 크기와 일치하는 (N_train,) 크기의 1차원 벡터가 생성됩니다.
X_valid = torch.stack([valid[i][0] for i in range(len(valid))]) # 검증(Valid) 데이터셋에 대해서도 동일한 과정을 거쳐 X_valid → (N_valid, 3, 32, 32) 구조의 독립된 검증용 데이터 텐서 쌍을 완성합니다.
y_valid = torch.tensor(valid.targets, dtype=torch.long) # 검증(Valid) 데이터셋에 대해서도 동일한 과정을 거쳐 y_valid → (N_valid,) 구조의 독립된 검증용 데이터 텐서 쌍을 완성합니다.
# 제공 부분: 0~8은 Backbone, 9는 새 3클래스 Head입니다.
model = nn.Sequential(
    nn.Conv2d(3, 8, 3, padding=1, bias=False), nn.BatchNorm2d(8), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(8, 16, 3, padding=1, bias=False), nn.BatchNorm2d(16), nn.ReLU(),
    nn.AdaptiveAvgPool2d((4, 4)), nn.Flatten(), nn.Linear(256, 3),
)
# 안전한 수치 배열만 읽습니다. Target 이미지로 사전학습한 파일이 아닙니다.
with np.load(DATA / "source_backbone.npz", allow_pickle=False) as saved: # 파일 입출력 안정성을 위해 with 문을 사용하여 source_backbone.npz 파일을 안전하게 열고 닫습니다.
                                                                         # allow_pickle=False를 통해 임의의 유해 코드 실행을 방지하는 보안 규칙을 준수합니다.
    state = model.state_dict()
    state.update({name: torch.from_numpy(saved[name].copy()) for name in saved.files}) # .npz 파일에 저장된 각 레이어의 가중치 이름(name)들을 순회하며 NumPy 배열을 PyTorch 텐서로 바꾼 뒤, 현재 정의된 model의 가중치 딕셔너리에 덮어씌웁니다.
model.load_state_dict(state) # 주입 가공이 끝난 state 가중치 맵을 최종적으로 모델에 완전히 로드합니다.
# requires_grad는 가중치 갱신, eval()은 BatchNorm 통계 사용 방식을 제어합니다.
for p in model.parameters(): # 모델 내부의 모든 파라미터(가중치와 편향)의 그래디언트 계산을 비활성화합니다.
                             # 역전파 시 이 레이어들은 오차 유도 계산에서 제외됩니다.
    p.requires_grad = False
for p in model[9].parameters(): # 앞서 정의하셨던 model의 9번째 인덱스 레이어는 nn.Linear(256, 3)입니다.
                                # 이 최종 분류 레이어의 가중치만 그래디언트 계산을 다시 활성화(True)하여 학습이 가능하도록 깨워줍니다.
    p.requires_grad = True
model.eval()  # 고정 Backbone의 running 통계도 보존
              # 모델을 평가(Inference) 모드로 전환합니다.
              # 앞서 정의한 모델에 포함된 nn.BatchNorm2d 레이어들이 학습 데이터의 통계값에 영향을 받지 않고 고정된 채로 동작하도록 고정해 주는 필수적인 역할을 합니다. (단, 파인 튜닝 중 출력층 학습 시 배치 정규화의 작동 방식에 따라 model.train()함수와 조율이 필요할 수 있습니다.)
optimizer = torch.optim.AdamW(model[9].parameters(), lr=0.01, weight_decay=0.0) # • 가중치 감쇠 감도가 개선된 최적화 알고리즘인 AdamW를 선언하되, 오직 9번째 분류 레이어의 파라미터들만 관리하도록 위임하고 학습률(Learning Rate)은 0.01로 지정합니다.
criterion = nn.CrossEntropyLoss()

history = [] # 매 에포크마다의 성능 기록을 누적할 리스트를 만듭니다.
best_loss = float("inf") # 최저 손실값을 비교하기 위해 best_loss 변수를 컴퓨터가 표현할 수 있는 가장 큰 값인 양의 무한대(inf)로 초기화합니다.
for epoch in range(1, 9):
    optimizer.zero_grad() # PyTorch는 이전 스텝에서 계산한 그래디언트(기울기)를 누적하는 성질이 있습니다.
                          # 이번 에포크의 순수한 기울기를 얻기 위해 기존에 남아있던 값들을 0으로 깨끗이 비워줍니다.
    loss = criterion(model(X_train), y_train) # 훈련 데이터 X_train을 모델에 넣어 나온 예측값과 정답 y_train 사이의 오차(loss)를 계산합니다.
                                              # 그 후 backward()를 호출하여 오차가 거꾸로 타고 올라가며 가중치들이 수정되어야 할 방향(기울기)을 계산합니다.
    # TODO B07: 역전파와 Optimizer 갱신을 수행하세요.
    # BEGIN B07
    loss.backward()  # loss.backward()와 optimizer.step() 두 문장을 작성하세요.
    optimizer.step() # 앞서 계산된 기울기와 지정한 학습률(lr=0.01) 및 AdamW 알고리즘을 바탕으로, 실제 모델 내부에서 동결되지 않은 유일한 레이어인 9번째 레이어(Linear)의 가중치를 물리적으로 업데이트합니다.
    # END B07
    with torch.no_grad():
        valid_loss = criterion(model(X_valid), y_valid).item() # 그래디언트 계산이 꺼진 상태에서 검증 데이터 X_valid를 넣어 오차를 구합니다.
                                                               # .item()은 텐서 형태의 손실 값을 파이썬의 순수한 실수(Float) 데이터로 변환해 줍니다.
    history.append({"epoch": epoch, "valid_loss": valid_loss})
    if valid_loss < best_loss: # 방금 계산한 valid_loss가 기존에 우리가 알고 있던 역대 최저 손실(best_loss)보다 작다면 기록을 갱신합니다.
                               # 그리고 그때의 에포크 번호와 가중치 정보(state_dict)의 스냅샷을 찍어 best_state에 저장합니다.
                               # 루프가 종료되면 가장 성적이 좋았던 best_state를 모델에 최종 이식합니다.
        best_loss = valid_loss
        best_epoch = epoch
        best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
model.load_state_dict(best_state) # 가장 성적이 좋았던 시점의 가중치를 모델에 덮어씌웁니다.
with torch.no_grad(): # 평가 단계이므로 메모리를 절약하고 속도를 높이기 위해 그래디언트 계산을 비활성화합니다.
    logits = model(X_valid)
    probabilities = logits.softmax(1) # 모델의 출력(Logits)을 클래스별 probabilities(확률값)로 변환하고 가장 확률이 높은 클래스 번호를 predictions(최종 예측값)으로 선택합니다.
    # TODO B08: 각 행의 가장 큰 logit 열을 예측 라벨로 고르세요.
    # BEGIN B08
    predictions = logits.argmax(dim=1)  # argmax로 바꾸세요.
    # END B08
metrics = {"accuracy": accuracy_score(y_valid, predictions), "macro_f1": f1_score(y_valid, predictions, labels=[0,1,2], average="macro", zero_division=0), "best_epoch": best_epoch, "valid_n": len(valid), "source": "synthetic_source_pretraining", "test_used": False} # 사이킷런(Scikit-learn)을 이용해 정확도와 불균형 데이터에 강한 Macro F1-score를 계산합니다.(zero_division=0으로 설정하여 분모가 0이 되는 에러를 방지함)
pd.DataFrame([metrics]).to_csv(OUT / "metrics.csv", index=False) # 동일한 평가지표 데이터를 다각도로 활용할 수 있게 가독성이 좋은 JSON과 데이터프레임용 CSV 두 가지로 저장합니다.
pd.DataFrame(history).to_csv(OUT / "history.csv", index=False) # 전체 학습과정의 Epoch별 Loss, Accuracy 기록을 저장합니다.
pd.DataFrame({"file": [Path(p).name for p,_ in valid.samples], "actual": y_valid.numpy(), "predicted": predictions.numpy(), "confidence": probabilities.max(1).values.numpy()}).to_csv(OUT / "predictions.csv", index=False) # valid.samples 명령어로 검증 데이터셋의 파일 경로에서 Path(p).name만 쏙 뽑아냅니다.
                                                                                                                                                                                                                             # probabilities.max() 함수를 통해 모델이 최종 선택한 클래스에 대해 몇 %의 확신을 가졌는지(Confidence) 추출합니다.('1'을 대입해 가로축(행 단위)최대값을 찾아라고 명령)
                                                                                                                                                                                                                             # 분석가는 이 predictions.csv를 열어 "모델이 99% 확신했는데 틀린 데이터" 위주로 보며 데이터 라벨링 오류나 모델의 치명적인 약점을 찾아낼 수 있습니다.
# TODO B09: metrics를 UTF-8 JSON 문자열로 저장하세요. 아래 제공된 경로를 사용합니다.
# BEGIN B09
with open(OUT / "metrics.json", "w", encoding="utf-8") as f:  # write_text로 metrics JSON을 저장하세요.
    json.dump(metrics, f, ensure_ascii=False, indent=4)
# END B09
pd.DataFrame(confusion_matrix(y_valid, predictions, labels=[0,1,2]), index=valid.classes, columns=valid.classes).to_csv(OUT / "confusion.csv") # 어떤 클래스를 오인했는지(예: 0번 클래스를 2번으로 착각했는지) 격자 형태로 보여주는 오차 행렬을 만듭니다.
                                                                                                                                               # 행과 열의 이름을 valid.classes(클래스 명칭)으로 지정하여 가독성을 높였습니다.
for old in OUT.glob("project_error_*.png"):
    old.unlink() # 이전 실행 때 생성된 예전 오답 이미지 파일들을 깔끔하게 삭제(초기화)합니다.
errors = (predictions != y_valid).nonzero().flatten().tolist() # 예측과 정답이 다른 틀린 데이터의 인덱스만 추려냅니다.
for i in errors[:8]:
    image = (X_valid[i].permute(1,2,0).numpy()*255).astype(np.uint8) # permute(1, 2, 0): PyTorch의 이미지 차원 순서([Channels, Height, Width])를 시각화 라이브러리 포맷인 [Height, Width, Channels]로 변경합니다.
                                                                     # *255.astype(np.uint8): 0~1 사이로 정규화되어 있던 텐서 값을 0~255 스케일의 이미지 픽셀 데이터로 복원합니다.
    cv2.imwrite(str(OUT / f"project_error_{i:02d}.png"), cv2.cvtColor(image, cv2.COLOR_RGB2BGR)) # PyTorch의 RGB 순서를 OpenCV의 표준인 BGR 순서로 뒤집어 색상이 왜곡되지 않게 이미지 파일로 저장합니다.(최대 8개까지 저장)
index = errors[0] if errors else 0 # 추후 코드나 노트북에서 첫 번째 오답 샘플을 바로 확인해 볼 수 있도록 errors[0] 값을 저장하며 마무리됩니다.
# hook 대신 Sequential을 둘로 나눕니다. 관심 클래스의 logit을 미분합니다.
image = X_valid[index:index + 1].clone().requires_grad_(True) # requires_grad_() 함수로 특정 이미지 영역에 대한 미분(그래디언트)을 구하기 위해 추적을 활성화합니다.
features = model[:7](image) # 모델을 두 부분으로 분리합니다. 앞부분은 이미지의 feature(특징맵)을 뽑아냅니다.
logits_one = model[7:](features) # 뒷부분은 앞에서 뽑아낸 특징을 바탕으로 최종 예측값(logits_one)을 만듭니다.
target = int(logits_one.argmax(1).item()) # 모델이 이 이미지에 대해 가장 높은 확률로 예측한 클래스 번호를 가져옵니다.
                                          # 오답 분석이므로 이 타겟은 틀린 예측값일 가능성이 높습니다.
gradient = torch.autograd.grad(logits_one[0, target], features)[0] # 선택한 target 클래스의 점수를 높이기 위해, 중간 features가 어떻게 변해야 하는지 Gradient를 구합니다.
weights = gradient.mean(dim=(2, 3), keepdim=True) # mean(dim=(2,3)): 구한 그래디언트 배열의 가로, 세로 평면에 대해 평균을 냅니다.
                                                  # 이를 통해 각 채널(특징 필터)이 이 예측에 얼마나 중요한 기여를 했는지 전역적인 weights(가중치)를 얻습니다.
cam = (weights * features).sum(dim=1).relu() # 중요하게 작용했던 채널 정보들을 가중치를 곱해 하나로 합칩니다.
                                             # relu() 함수로 클래스 판단에 긍정적인 영향을 준 Positive Influence(양의 반응) 구역만 남기고 음수 값은 0으로 날립니다.
cam = torch.nn.functional.interpolate(cam.unsqueeze(1), size=(32, 32), mode="bilinear", align_corners=False)[0, 0] # 해상도가 낮아진 특징 맵 크기를 원본 이미지크기(32 X 32로 추정)에 맞게 양선형 보간법으로 확대합니다.
cam = cam.detach().numpy()
cam = cam / max(float(cam.max()), 1e-8)  # 양의 반응이 없으면 0 지도를 유지
                                         # 최댓값으로 나누어 0 ~ 1 사이로 정규화합니다.
                                         # 만약 양의 반응이 전혀 없는 빵점짜리 지도라면 분모가 0이 되어 터지는 것을 막기 위해 1e-8 장치를 둡니다.
rgb = (X_valid[index].permute(1, 2, 0).numpy() * 255).astype(np.uint8)
heat_bgr = cv2.applyColorMap(np.uint8(cam * 255), cv2.COLORMAP_JET) # 0 ~ 1 스케일의 중요도 정보를 파란색(낮음)부터 빨간색(높음)까지의 열지도(Heatmap) 영상으로 바꿉니다.
overlay = cv2.addWeighted(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), 0.6, heat_bgr, 0.4, 0) # 원본 BGR 이미지(60%)와 히트맵 이미지(40%)를 투명하게 겹쳐서 투영합니다.

cv2.imwrite(str(OUT / "project_cam.png"), cv2.resize(overlay,(256,256))) # 32 x 32 크기는 사람이 보기에 너무 작으므로, 식별이 잘 되도록 256 x 256 크기로 키워서 project_cam.png 파일로 저장합니다.
print(json.dumps(metrics,ensure_ascii=False,sort_keys=True))
print("오답 수:",len(errors),"예측 행:",len(valid),"test 사용: False")
