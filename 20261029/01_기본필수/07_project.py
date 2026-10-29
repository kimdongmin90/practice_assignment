"""실습 07~08: 정상 데이터 20건. train 12건 학습, valid 4건 확인, test 4건 보관."""
from pathlib import Path
import csv
import json
import torch
from torch import nn

# 파일 위치를 기준으로 읽으므로 다른 작업 폴더에서 실행해도 됩니다.
base = Path(__file__).resolve().parent # pathlib.Path() 함수를 통해 코드가 들어있는 폴더 안에서 points.csv의 정확한 주소를 찾습니다.(현재 실행 중인 파이썬 파일이 있는 "부모 폴더"의 절대 주소를 자동으로 알아냅니다.)
with (base / "points.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f)) # csv.DictReader() 함수를 통해 points.csv 파일에서 엑셀의 한 줄 한 줄 텍스트 데이터를 딕셔너리 리스트(키: 값) 구조로 변환해서 row에 담아둡니다.
train_rows = [r for r in rows if r["split"] == "train"] # 전체 데이터 중 split 방에 train이라고 적힌 데이터만 골라냅니다.
valid_rows = [r for r in rows if r["split"] == "valid"] # 전체 데이터 중 split 방에 valid라고 적힌 데이터만 격리합니다.
X_train = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in train_rows]) # 각 데이터에서 입력 특징 x1과 x2를 문자열에서 float로 바꾼 뒤, 2차원 행렬 텐서로 만듦니다.
y_train = torch.tensor([int(r["label"]) for r in train_rows], dtype=torch.long) # 정답 번호인 label을 int로 바꾼 뒤, 파이토치 분류 정답 표준 규격인 dtype=torch.long 텐서로 만듦니다.
X_valid = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in valid_rows]) # X_train과 같은 방식으로 만듦니다.
y_valid = torch.tensor([int(r["label"]) for r in valid_rows], dtype=torch.long) # y_train과 같은 방식으로 만듦니다.
# 기본필수는 CPU 고정, full-batch 80회입니다. test는 Tensor로 만들지 않습니다.
torch.manual_seed(42) # torch.manual_seed() 함수를 이용해 언제 실행해도 같은 결과가 나오도록 무작위 가중치 시작점을 고정합니다.
model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2)) # nn.Linear() 함수를 이용해서 2개의 입력을 8개의 다른 관점으로 조합하고 생각해보는 첫번째 인공신경망(은닉층)입니다.
                                                                   # nn.ReLU() 활성화 함수로 음수(-)는 0으로 지워버리고 양수(+) 신호만 통과시키며 인공지능에게 생각의 유연함을 줍니다.
                                                                   # nn.Linear() 함수를 다시 이용해서 8개로 확장했던 생각을 모아 최종적으로 2개의 결론(0번일 확률, 1번일 확률)으로 압축합니다.
                                                                   # nn.Sequential(...) 함수를 이용해 위에서 만든 층(방과 필터)을 순서대로 이어 붙여 하나의 모델(인공지능 뇌)로 조립합니다. 
loss_fn = nn.CrossEntropyLoss() # nn.CrossEntropyLoss() 함수로 AI가 정답을 맞추면 Loss을 낮게 주고, 틀리거나 헷갈려 하면 Loss를 높게 줍니다.
optimizer = torch.optim.SGD(model.parameters(), lr=0.1) # torch.optim.SGD() 함수로 AI의 틀린 생각을 고쳐줍니다.
                                                        # lr=0.1(학습률)은 한 번 고칠 때 얼마나 큰 폭으로 고칠지 결정하는 '학습 속도'입니다.
history = [[0, loss_fn(model(X_train), y_train).item()]] # 파이토치가 갖고 있는 (tensor(...))에 쌓여 있는 Loss값을 읽기 편한 숫자(예: 0.74)로 loss.item() 함수로 꺼냅니다.
model.train() # model.train() 함수로 인공지능에게 가중치를 바꾸며 학습할 것을 알립니다.
for epoch in range(1, 81): # for 반복문을 이용해 epoch(처음부터 끝까지 학습완료)를 80회 시행합니다.
    optimizer.zero_grad() # 새 학습에 앞서 optimizer.zero_grad() 함수로 앞서 학습한 gradients(기울기)를 지웁니다.
    loss = loss_fn(model(X_train), y_train)
    # 06번에서 배운 역전파와 파라미터 갱신 두 문장을 연결하세요.
    # 이미 위에서 이전 gradient를 비우고 loss를 계산했습니다.
    # >>> B08
    # TODO B08: 위 요구사항을 읽고 이 블록을 완성하세요.
    loss.backward() # 결과로 나온 loss값을 가지고 loss.backwar() 함수로 어디서 잘못됐는지 신경망을 거꾸로 타고 올라가며 미분 계산기로 원인을 추적합니다.
    optimizer.step() # 원인 분석이 끝나고 optimizer.step() 함수로 Parameters(가중치)를 업데이트 합니다.
    # <<< B08
    # 갱신 후 같은 train 자료의 loss를 기록합니다. 마지막 batch loss와 구분합니다.
    with torch.no_grad(): # 학습이 완전히 끝나고 불필요한 메모리 낭비를 막고 안전하게 최종 결과만 확인합니다.
        history.append([epoch, loss_fn(model(X_train), y_train).item()])
model.eval() # model.eval() 명령어로 학습을 끝내고 평가를 준비합니다.
with torch.no_grad():
    logits = model(X_valid)
    # 각 행에서 가장 큰 logit의 열 번호를 prediction으로 구하세요.
    # argmax의 dim=1은 클래스 방향입니다. 결과 shape는 (4,)입니다.
    # >>> B09
    # TODO B09: 위 요구사항을 읽고 이 블록을 완성하세요.
    prediction = logits.argmax(dim=1) # 행 방향(위에서 아래)이 아닌 가로축 열 방향(왼쪽에서 오른쪽, 클래스 방향)으로 가장 큰 값을 추적해야 하므로 dim=1 옵션을 지정합니다.
                                      # logits.argmax(...) 파이토치 전용 함수를 이용해 인자로 준 방향을 따라 가장 큰 숫자가 들어있는 인덱스를 정수로 반환합니다.
    # <<< B09
    accuracy = (prediction == y_valid).float().mean().item() # AI 리스트와 진짜 리스트를 위에서부터 하나씩 1:1로 비교합니다.
                                                             # [True, True, False, True]라는 컴퓨터용 통과/탈락 신호가 만들어집니다.
                                                             # True와 False 상태로는 수학 계산을 못하므로 .float() 함수로 강제 변환합니다.
                                                             # [1.0, 1.0, 0.0, 1.0] 결과가 나옵니다.
                                                             # .mean() 함수로 앞에 만든 점수들을 다 더한 뒤 전체 문제 수(4문제)로 나눠 평균을 구합니다.
                                                             # (1.0 + 1.0 + 0.0 + 1.0) / 4 = 3.0 / 4 = 0.75
                                                             # 앞서 계산된 tensor(0.75)에 담긴 값을 .item() 함수로 꺼낸 순수한 숫자 0.75를 accuracy에 저장합니다. 
with (base / "training_history.csv").open("w", encoding="utf-8-sig", newline="") as f: # 지정해 둔 base(현재 작업 폴더)안에 training_history.csv라는 이름의 새 파일을 만들 주소를 지정합니다.
                                                                                       # .open(, ...) 함수를 이용하여 "w"(쓰기) 상태로 기존 내용을 다 지우고 새로 쓰거나 파일이 없다면 새로 만듦니다.
                                                                                       # 한국어가 포함된 데이터 저장 시, 엑셀 프로그램에서 글자가 깨지지 않고 정상적으로 한글과 기호가 보이도록 방지할 수 있게 encoding="utf-8-sig" 명령어로 전용 안전 포맷 덮개 처리합니다.
                                                                                       # 엑셀 파일 저장 시 줄 바꿈이 두 번씩 일어나 한 줄씩 빈칸이 생기는 버그를 막기 위해 newline="" 명령어로 처리합니다.
                                                                                       # 앞선 길고 복잡한 파일 열기 설정을 파이썬 코드 안에서 앞으로 가볍게 f로 부르기 위해 as f 명령어를 이용합니다.
    writer = csv.writer(f)  # 방금 열어둔 파일 f에 csv.writer() 함수를 이용해서 데이터를 적어줍니다.
    writer.writerow(["epoch", "train_loss_eval"]) # writer.writerow(...) 함수로 딱 한줄(row)만 먼저 인쇄하라고 명령합니다.(엑셀의 맨 첫 행에 제목으로 쓸 컬럼명들을 가로로 나란히 채워 넣습니다.) -> 단수형
    writer.writerows(history) # writer.writerows() 함수로 그동안 모아둔 history(80줄짜리 리스트)를 넘겨주며 나머지 모든 줄(rows)을 복사 붙여넣게 합니다. -> 복수형
metrics = {"device": "cpu", "epochs": 80, "train_rows": 12, "valid_rows": 4,
           "test_used": False, "valid_accuracy": accuracy,
           "initial_train_loss": history[0][1], "final_train_loss": history[-1][1],
           "valid_ids": [r["id"] for r in valid_rows], "actual": y_valid.tolist(),
           "predicted": prediction.tolist()} # metrics라는 이름의 딕셔너리(key-value 쌍) 주머니를 열고 모델의 모든 정보를 수집하기 시작합니다.
                                             # "device"라는 방에 이번 인공지능 연산에 사용한 하드웨어 장치 장소('cpu')를 기록합니다.
                                             # "epochs"라는 방에 교과서를 총 몇 바퀴 돌며 반복 학습(80회)했는지 정수를 저장합니다.
                                             # "train_rows"라는 방에 평소 훈련 및 학습용으로 사용한 데이터 샘플 개수(12건)를 기록합니다.
                                             # "valid_rows"라는 방에 모의고사용으로 격리해 두었던 데이터 샘플 개수(4건)를 기록합니다.
                                             # "test_used"라는 방에 수능 시험지인 test 세트를 미리 열어보는 반칙을 했는지 여부(False)를 기록합니다.
                                             # "valid_accuracy"라는 방에 앞서 계산해 둔 모의고사 최종 정답률 점수(accuracy 변숫값)를 담아둡니다.
                                             # 공부를 시작하기 전(0번째 에포크) AI가 기록했던 최초의 오차 벌점(history의 첫 줄의 점수값)을 저장합니다.
                                             # 80바퀴 공부가 모두 완전히 종료된 후 최종 기록된 마지막 오차 벌점(history의 마지막 줄의 점수값)을 저장합니다.
                                             # 리스트 컴프리헨션을 발동해 모의고사 데이터(valid_rows) 주머니를 돌며 각 데이터의 고유 식별 번호('id')만 뽑아 리스트로 저장합니다.
                                             # 파이토치 전용 상자에 갇혀있던 실제 모의고사 진짜 정답지(y_valid 텐서)를 순수 파이썬 리스트로 변환(.tolist())하여 저장합니다.
                                             # 인공지능이 argmax로 열심히 찍어낸 최종 모의고사 예측 번호(prediction 텐서)를 순수 파이썬 리스트로 변환(.tolist())하여 저장합니다.
(base / "final_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8") # 취합된 metrics 주머니를 가독성 좋은 JSON 글자 묶음으로 변환한 뒤, final_metrics.json 파일에 문자열로 영구 저장합니다.
(base / "gpu_check.txt").write_text( # 이번 실행 단계에서 사용한 파이토치 버전 및 쿠다(GPU) 연동 정보를 f-string을 활용해 하나의 거대한 줄글 텍스트로 만듭니다.
    f"torch={torch.__version__}\ncuda_build={torch.version.cuda}\n" # f-string 문자열 내부에서 파이토치 버전 번호를 변수로 치환하여 첫 번째 줄 텍스트를 구성합니다.
                                                                    # 내부에 탑재된 CUDA 그래픽카드 특수 기술의 빌드 버전을 두 번째 줄 텍스트로 연동합니다.
    f"cuda_available={torch.cuda.is_available()}\nselected_device=cpu\n", encoding="utf-8") # 그래픽카드 장치를 진짜로 활성화해서 쓸 수 있는지 여부(True/False)를 세 번째 줄에 얹어줍니다.
                                                                                            # 최종 수동 지정해서 사용한 연산 엔진이 'cpu' 공간임을 마지막 줄에 명시하며 줄바꿈(\n)을 닫습니다.
                                                                                            # 텍스트 파일을 하드디스크에 저장할 때 전 세계 웹 표준 한글 포맷인 'utf-8' 규격으로 문을 잠그고 파일을 생성합니다.
print("분할: train 12 / valid 4 / test 4(보관)") # 콘솔창에 "전체 20건의 데이터 중 공부용 12건, 모의고사용 4건, 비밀 수능용 4건이 안전하게 격리 분할되었다"고 인쇄합니다.
print("train loss:", round(history[0][1], 6), "->", round(history[-1][1], 6)) # 소수점 6번째 자리까지 이쁘게 둥글린(round) 처음 오차 점수와 마지막 오차 점수를 나란히 출력하여 오차가 잘 떨어졌는지 보여줍니다.
print("valid 정확도:", round(accuracy, 4)) # 모의고사 채점 결과 나온 최종 정확도(Accuracy 소수점) 수치를 깔끔하게 소수점 4자리까지 반올림(round)해서 눈으로 확인시켜 줍니다.
print("valid 예측:", prediction.tolist()) # 파이토치 텐서 포장 상자 안에 들어있던 인공지능의 4문제짜리 정답 예측 번호를 순수 파이썬 리스트로 풀어헤쳐서 가볍게 찍어줍니다.
print("생성: gpu_check.txt, training_history.csv, final_metrics.json") # 전체 과정이 안전하게 종료되어 하드디스크에 보고서 파일 3개가 에러 없이 온전하게 잘 구워졌음을 최종 보고하며 마감합니다.
