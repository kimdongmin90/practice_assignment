import torch
from torch import nn
torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
                          # torch.set_num_threads() 함수로 멀티스레딩으로 인한 CPU 연산 속도의 가변성을 통제하고 자원을 격리합니다.
                          # 교육용 실습 환경이나 가벼운 CPU 벤치마크 테스트를 진행할 때, 환경에 상관없이 일관된 실행 조건과 연산 타이밍을 보장하기 위함입니다.
torch.manual_seed(42) # 파이토치 내부의 난수 생성 엔진의 시드(Seed) 값을 고정합니다.
                      # 모델 가중치를 초기화하거나 데이터를 셔플할 때 발생할 수 있는 무작위성을 제어하여, 코드를 다시 실행해도 완전히 동일한 실험 결과를 얻기 위함입니다.
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent # 현재 실행중인 (__file__)(스크립트 파일 파일명)을 기준으로 삼아 resolve() 함수로 절대경로를 추적하고, parent(부모 폴더)의 위치를 ROOT에 할당합니다.
                                       # 'C:/Users/...' 같은 하드코딩된 절대 경로는 다른 컴퓨터에서 코드가 작동하지 않습니다.
                                       # 이 방식을 쓰면 프로젝트 폴더가 어떤 환경(Windows, Mac, Linux)으로 이동하더라도 경로 에러 없이 series.csv 파일을 정확하게 로드할 수 있습니다.
df = pd.read_csv(ROOT / "series.csv")
# 시간 구간을 먼저 분리한다. test 구간은 모델에 넣지 않는다.
train = torch.tensor(df.loc[df["split"]=="train","value"].values,dtype=torch.float32) # Pandas의 .loc 인덱서를 사용해 split 열의 값이 "train"인 행을 필터링하고, 예측 대상인 "value"열의 데이터만 추출한뒤 .value 명령어를 통해 Numpy Array로 변환합니다.
                                                                                      # 이미지나 일반 정형 데이터는 Random으로 훈련/검증 세트를 쪼개지만, 시계열 데이터는 반드시 과거 데이터로 학습하여 미래 데이터를 검증해야 합니다.
                                                                                      # 데이터에 이미 정의된 시계열 순서(split 조건)에 따라 순차적으로 데이터를 안전하게 나누는 접근 방식입니다.
                                                                                      # 평가(Test) 구간은 모델이 미리 들여다보지 못하도록 격리해 둡니다.
                                                                                      # 추출된 넘파이 데이터를 파이토치 연산의 기본 단위인 Tensor로 변환하면서 데이터 타입을 float32(32비트 부동소수점 실수형)로 강제 지정합니다.
                                                                                      # 판다스나 넘파이의 실수는 기본적으로 float64 또는 double(64비트)인 경우가 많습니다.
                                                                                      # 파이토치의 선형 레이어나 LSTM 같은 신경망 계층은 기본 가중치 타입으로 float32를 표준으로 채택하고 있습니다.
                                                                                      # 따라서 이 변환을 미리 하지 않으면 나중에 모델에 데이터를 입력할 때 'RuntimeError: Expected object of scalar type Float but got Double' 같은 타입 불일치 에러를 마주하게 됩니다.
valid = torch.tensor(df.loc[df["split"]=="valid","value"].values,dtype=torch.float32)

x = train.unfold(0,8,1).contiguous() # 별도의 for 루프 없이, 파이토치 내장 함수인 .unfold(dimension, size, step)를 사용하여 1차원 시계열 벡터를 윈도우 크기 8, Stride(이동 간격) 1의 2차원 행렬로 순식간에 잘라냅니다.
                                     # 연속적인 과거 데이터를 한 행에 모아([t0, t1, ..., t7], [t1, t2, ..., t8] 형태) 모델이 패턴을 학습하게 만듭니다.
                                     # .contiguous()는 슬라이싱 과정에서 바뀐 데이터 메모리 주소(Stride 구조)를 연속적인 상태로 재정렬하여 이후 딥러닝 연산에서 에러가 발생하지 않도록 물리적 배치를 최적화하는 필수 작업입니다.
                                     # (원래 길이 - 윈도우 크기) / 스트라이드 + 1 법칙에 따라 (100 - 8) / 1 + 1 = 93 행을 가진 (93, 8) 크기의 텐서가 됩니다.
v = valid.unfold(0,8,1).contiguous()
model = nn.Sequential(nn.Linear(8,2),nn.Tanh(),nn.Linear(2,8)) # nn.Linear() 함수로 8차원의 입력 윈도우 데이터를 단 2차원의 압축된 핵심 공간(잠재 공간, Latent Space)으로 압축합니다.(Encoder)
                                                               # nn.Tanh() 함수로 거치며 데이터에 비선형성을 부여하고 압축된 값을 [-1, 1] 범위로 고정합니다.
                                                               # nn.Linear() 함수로 압축되었던 2차원의 특징을 다시 원래 크기인 8차원의 신호로 복원(Reconstruction)합니다.(Decoder)
                                                               # 데이터의 차원을 줄였다가다시 원복하는 과정에서 모델은 노이즈를 버리고 데이터의 핵심적인 규칙과 패턴을 스스로 학습하게 됩니다.
optimizer = torch.optim.Adam(model.parameters(),lr=0.03) # 이전 Epoch에서 계산되어 메모리에 남아있던 Gradient 값을 optimizer.zero_grad() 함수로 비워주어 새로운 연산을 준비합니다.
for epoch in range(40):
    optimizer.zero_grad()
    reconstructed = model(x)
    # TODO B04: Autoencoder의 정답을 입력 x 자체로 설정한다.
    # 정상 데이터를 0으로 바꾸는 과제가 아니다. reconstruction과 x를 비교한다.
    # BEGIN B04
    loss = nn.MSELoss()(reconstructed, x) # nn.MSELoss()(모델이 복원해 낸 예측값, 실제 원본 입력값) 함수로 reconstructed(모델이 복원해 낸 예측값)과 x(실제 원본 입력값) 사이의 평균 제곱 오차(MSE)를 구합니다.
                                          # 정답 데이터가 따로 주어지지 않고 자기 자신을 정답으로 두고 풀기 때문에 Self-Supervised(비지도 학습)에 해당합니다.
    # END B04
    loss.backward() # loss.backward() 함수로 오차에 대한 미분값을 계산(역전파)합니다.
    optimizer.step() # optimizer.step() 함수로 Adam 옵티마이저를 가동하여 모델의 가중치를 정밀하게 업데이트 합니다.
model.eval() # model.eval() 함수로 모델을 평가모드로 전환합니다. 
with torch.inference_mode(): # torch.inference_mode() 함수로 메모리를 소모하는 기울기 계산 그래프 생성을 차단(inference_mode)하여 검증 연산 속도를 극대화합니다.
    latent = model[:2](v) # 전체 3개의 층 중에서 인코더 부분인 [0번 Linear, 1번 Tanh] 층까지만 슬라이싱([:2])하여 검증 데이터 v를 통과시킵니다.
                          # 디코더를 거치기 전, 모델이 데이터를 어떻게 'latent.shape -> (13, 2)'(2차원 특징)으로 추상화했는지 중간 결과물(임베딩 벡터)을 뽑아내기 위함입니다.(추후 시각화나 이상치 탐지의 feature로 활용됩니다.)
    error = nn.MSELoss()(model(v),v).item()
print("train:", tuple(x.shape), "valid:", tuple(v.shape))
print("latent / 복원:", tuple(latent.shape), tuple(model(v).shape))
print("valid MSE:", round(error,6))
