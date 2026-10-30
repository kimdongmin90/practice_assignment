from pathlib import Path # FileNotFoundError 같은 경로 에러를 원천 차단하고, Path(__file__).resolve().parent 기법을 통해 코드가 실행되는 현재 폴더의 위치를 정확하게 조준하기 위해 from pathlib import Path 명령어를 사용합니다.
import pandas as pd # 수집된 요청 데이터(requests.csv)나  학습용 포인트 데이터(pints.csv)를 pd.read_csv() 함수 한줄로 긁어 슬라이싱, 필터링, 새로운 열(예: 로그 변환 열) 추가 등을 자유자재로 하기 위해 import pandas as pd 명령어로 표(DataFrame) 형태의 데이터를 조작하는 데이터 과학의 필수 라이브러리를 pd라는 짧은 별명으로 불러 사용합니다.
import torch # 파이썬 기본 리스트가 할 수 없는 대규모 병렬 행렬 연산과 역전파 자동 미분(backward()) 시스템을 지원하는 핵심 데이터 구조인 텐서(Tensor)를 생성하고 제어하기 위해 반드시 선언해야 하는 Meta에서 개발한 오픈소스 딥러닝 프레임워크입니다.
from torch import nn # nn.Linear(선형 연결층), nn.ReLU(활성화 함수 필터), nn.CrossEntropyLoss(객관식 표준 채점기) 등 인공지능의 뇌 세포 구조와 시험지를 설계할 때 필요한 부품들을 곧바로 꺼내 쓰기 위해 PyTorch내에서 신경망(Neural Network)을 구성하는 레이어와 모듈들이 담겨있는 핵심 상자에서 불러옵니다.

torch.set_num_threads(1) # 파이토치가 CPU 연산을 할 때 여러 개의 스레드를 쓰지 않고 오직 1개의 스레드만 쓰도록 강제 고정합니다.
                         # 자원이 제한된 시험장 환경이나 디버깅 시 연산의 일관성을 보장합니다.
base = Path(__file__).resolve().parent
df = pd.read_csv(base / "points.csv") # 판다스를 이용해 base(현재 폴더)에 있는 points.csv 파일을 읽어와 행과 열을 가진 df(데이터프레임)로 변환을 pd.read_csv(...) 함수로 합니다.
train = df[df["split"] == "train"] # split 열의 값이 "train"인 행들만 필터링해서 따로 떼어 놓습니다.
valid = df[df["split"] == "valid"] # split 열의 값이 "valid"인 행들만 필터링해서 따로 떼어 놓습니다.
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32) # 판다스 표의 껍데기(행 번호, 열 이름 글자 등)를 다 버리고 안에 순수한 숫자만 고속 넘파이(NumPy) 2차원 배열로 train["x1", "x2"].values 명령어로 뽑아냅니다.
                                                                        # 추출한 2차원 숫자를 파이토치 텐서로 감싸면서, 인공지능 세계의 연산 표준 실수 겨격인 "dtype=torch.float32"로 변환합니다.
y_train = torch.tensor(train["label"].values, dtype=torch.long) # 정답 번호가 들어있는 label 열의 내용을 뽑아내어, 파이토치 다중 분류의 표준 정수 규격인 dtype=torch.long(64비트 정수) 텐서로 변환합니다.
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32) # X_valid와 y_valid도 위와 동일한 메커니즘을 거쳐 고속 넘파이 배열 변환을 통해 파이토치 맞춤형 표준 텐서 세트로 빌드업됩니다.
y_valid = torch.tensor(valid["label"].values, dtype=torch.long)
# test 4건은 읽은 표에만 있으며 학습/평가 Tensor로 만들지 않습니다.

loss_fn = nn.CrossEntropyLoss()
for name in ["SGD", "AdamW"]:
    # 후보마다 같은 초기 가중치에서 다시 시작합니다. 앞 모델을 이어 학습하지 않습니다.
    torch.manual_seed(42)
    model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2))
    if name == "SGD": 
        # 학습률은 기본값에 기대지 않고 명시하며, 두 Optimizer 모두 weight_decay=0.0으로 비교합니다.
        # >>> B01
        # TODO B01: 위 요구사항에 맞게 이 블록만 완성합니다.

        optimizer = torch.optim.SGD(
        # SGD(Stochastic Gradient Descent, 확률적 경사하강법) 최적화기를 생성합니다.
        # loss.backward()가 각 파라미터의 .grad에 저장한 기울기를 이용하여, optimizer.step()을 호출할 때 가중치와 편향을 갱신합니다.
        # 한 번에 사용할 데이터의 개수는 SGD가 아니라 DataLoader의 batch_size로 정합니다.
        # SGD의 학습할 파라미터는 model.parameters()입니다. lr=0.01, momentum=0.0으로 만드세요.

            model.parameters(),
            # 갱신할 모델의 파라미터를 전달합니다.
            # 현재 모델에서는 각 Linear 층의 가중치(weight)와 편향(bias)이 해당합니다.
            # ReLU처럼 학습할 파라미터가 없는 층은 갱신 대상이 없습니다.
            
            lr=0.01,
            # 학습률(learning rate): 기울기를 이용해 파라미터를 얼마나 이동시킬지 정합니다.
            # momentum과 weight_decay가 0이면 다음 식으로 갱신합니다.
            # 새로운 파라미터 = 기존 파라미터 - 학습률 × 현재 기울기
            # 너무 크면 손실이 진동하거나 발산할 수 있고, 너무 작으면 학습이 느릴 수 있습니다.
            
            momentum=0.0,
            # 모멘텀(momentum): 이전 갱신 방향을 누적하여 현재 갱신에 반영하는 정도입니다.
            # 같은 방향의 기울기가 이어지면 이동을 가속하고,
            # 방향이 반복해서 바뀌는 구간에서는 진동을 줄이는 데 도움이 될 수 있습니다.
            # 0.0은 모멘텀을 사용하지 않는다는 뜻이며, 0.9 등이 자주 사용됩니다.
            
            weight_decay=0.0)
            # 가중치 감쇠(weight decay): 파라미터가 지나치게 커지는 것을 억제하는 규제입니다.
            # PyTorch의 SGD에서는 기울기에 "weight_decay × 현재 파라미터"를 더합니다.
            # 이는 L2 규제에 해당하며, 과적합을 줄이는 데 도움이 될 수 있습니다.
            # 0.0은 적용하지 않는다는 뜻이고, 너무 크게 설정하면 과소적합이 생길 수 있습니다.
            # 여기서는 model.parameters() 전체를 전달했으므로 편향에도 동일하게 적용됩니다.
            
        # <<< B01
    else:
        # AdamW를 같은 lr=0.01로 만드세요. weight_decay=0.0을 반드시 적으세요.
        # 이번에는 감쇠 효과가 아닌 갱신 규칙을 비교합니다. 이 공통 lr이 두 알고리즘의 최적 lr이라는 뜻은 아닙니다.
        # >>> B02
        # TODO B02: 위 요구사항에 맞게 이 블록만 완성합니다.
        
        optimizer = torch.optim.AdamW(
        # AdamW 최적화기를 생성합니다.
        # 각 파라미터에 대해 기울기의 이동평균과 기울기 제곱의 이동평균을 관리하고,
        # 이를 이용해 파라미터별 갱신 크기를 조절합니다.
        # loss.backward()로 기울기를 계산한 뒤 optimizer.step()으로 갱신합니다.
            
            model.parameters(),
            # 갱신할 모델의 파라미터를 전달합니다.
            # 현재 모델에서는 각 Linear 층의 가중치(weight)와 편향(bias)이 해당합니다.
            
            lr=0.01,
            # 학습률(learning rate): 파라미터 갱신 크기의 기본 배율입니다.
            # AdamW는 기울기의 이동평균과 제곱 이동평균을 이용하므로,
            # 단순히 "현재 기울기 × 학습률"만큼 이동하는 것은 아닙니다.
            # 같은 lr이라도 SGD와 AdamW의 실제 갱신 크기와 학습 결과는 다를 수 있습니다.
            # 너무 크면 학습이 불안정해지고, 너무 작으면 학습이 느려질 수 있습니다.

            weight_decay=0.0)
            # 가중치 감쇠(weight decay): 파라미터가 지나치게 커지는 것을 억제하는 규제입니다.
            # AdamW는 손실의 기울기에 규제 항을 더하는 대신,
            # 적응적 기울기 갱신과 분리하여 파라미터를 직접 줄입니다.
            # 감쇠 부분만 보면 "파라미터 *= (1 - lr × weight_decay)"에 해당합니다.
            # 과적합을 줄이는 데 도움이 될 수 있지만, 너무 크면 과소적합이 생길 수 있습니다.
            # 0.0은 가중치 감쇠를 적용하지 않는다는 뜻입니다.
            # 양수로 설정하면 여기서는 전달한 모든 파라미터에 적용되므로 편향도 감쇠됩니다.

        # AdamW에는 SGD의 momentum 대신 betas라는 설정이 있습니다.
        # 생략하면 기본값 betas=(0.9, 0.999)를 사용합니다.
        # 첫 번째 값: 기울기의 이동평균에 이전 정보를 얼마나 유지할지 결정합니다.
        # 두 번째 값: 기울기 제곱의 이동평균에 이전 정보를 얼마나 유지할지 결정합니다.
        # 따라서 weight_decay=0.0이어도 과거 기울기를 활용하는 기능은 작동합니다.

        # <<< B02
    for epoch in range(20):
        model.train()
        optimizer.zero_grad()
        loss = loss_fn(model(X_train), y_train)
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        valid_loss = loss_fn(model(X_valid), y_valid).item()
    print(name, "20 epochs / valid loss:", round(valid_loss, 6))
