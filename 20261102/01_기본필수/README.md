# 기본필수 · CNN을 짧은 코드로 확인하기

이 폴더에는 실습용 Python 8개와 README, ImageFolder에 필요한 `data/`만 있습니다. 사용자 정의 함수·클래스·예외처리는 만들지 않습니다. 생성되는 CSV·PT도 이 폴더에 저장합니다.

```text
01_기본필수/
  README.md
  01_tensor.py ... 08_project.py
  data/
    train/horizontal/  train/vertical/
    valid/horizontal/  valid/vertical/
    test/horizontal/   test/vertical/  ← 보관, 실행에 사용하지 않음
```

PPT의 `SmallCNN` 클래스 대신 같은 Conv16→Conv32→Global Pool→Head를 `nn.Sequential`로 제공합니다. 이번 자료는 두 클래스이므로 Head 출력은 2개입니다. 기본 학습 입력은 32×32, 5 epoch, CPU·정상 이미지입니다. 코드의 읽기·모델 생성·결과 저장은 제공되며 TODO 9곳만 직접 완성합니다.

한꺼번에 모든 파일을 읽지 말고 01→02→03→04→05→06→07→08 순서로 진행합니다. 01~07은 서로의 출력 파일에 의존하지 않습니다. 06은 사전학습 가중치가 준비된 경우만 실행하며 다른 파일을 막지 않습니다.

## 오늘 처음 만나는 API의 읽는 법

| 호출 | 하는 일 | 필수 인자 | 주요 선택 인자·기본값 |
|---|---|---|---|
| `torch.rand(4,3,32,32)` | 해당 모양의 난수 Tensor | 모양을 정하는 크기 | `dtype`, `device`; 여기서는 float32·CPU |
| `x.permute(1,2,0)` | 값은 그대로, 축 순서 변경 | 모든 축의 새 순서 | 추가 선택 인자 없음 |
| `x.unsqueeze(0)` | 크기 1의 축 추가 | `dim` | 추가 선택 인자 없음 |
| `nn.Conv2d(3,8,3,padding=1)` | 학습 가능한 필터로 특징 계산 | `in_channels, out_channels, kernel_size` | `stride=1, padding=0, dilation=1, groups=1, bias=True` |
| `nn.MaxPool2d(2)` | 작은 영역의 최댓값 선택 | `kernel_size` | `stride=None`이면 커널 크기 사용, `padding=0` |
| `nn.AdaptiveAvgPool2d(1)` | 채널별 목표 공간 크기로 평균 | `output_size` | 이 예제의 추가 선택 인자 없음 |
| `nn.Flatten()` | 공간 축을 긴 벡터로 합침 | 없음 | `start_dim=1, end_dim=-1` |
| `nn.Linear(32,2)` | 특성 32개를 클래스 점수 2개로 변환 | `in_features, out_features` | `bias=True` |
| `ImageFolder(root, transform=...)` | 클래스 폴더에서 이미지·라벨 읽기 | `root` | `transform=None`, `target_transform=None` |
| `Compose([...])` | 여러 변환을 차례대로 적용 | 변환 목록 | 없음 |
| `Resize((32,32))` | 입력 크기 변경 | `size` | `interpolation`, `antialias` 등 |
| `ToTensor()` | PIL 이미지→CHW float Tensor | 없음 | 없음; 이 PNG의 값은 보통 0~1 |
| `Normalize(mean,std)` | 채널별 `(x-mean)/std` | `mean`, `std` | `inplace=False` |
| `DataLoader(dataset, batch_size=4)` | 이미지들을 배치로 묶음 | `dataset` | `batch_size=1, shuffle=False, num_workers=0, drop_last=False` |
| `resnet18(weights=...)` | ResNet18 모듈 생성 | 필수 사용자 인자 없음 | `weights=None, progress=True`; 여기서는 실제 가중치를 명시 |
| `weights.transforms()` | 해당 사전학습 가중치의 변환 생성 | 필수 사용자 인자 없음 | 기본 Resize·Crop·Normalize 사용 |

층을 만드는 호출과 데이터를 넣는 호출은 다릅니다. `conv=nn.Conv2d(...)`로 층을 만들고 `y=conv(x)`로 계산합니다. `CrossEntropyLoss`에는 Softmax 이전 logits와 long 정수 라벨을 넣습니다.


## 실습 06 시작 전: 실제 사전학습 가중치 준비

`resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)`는 공식 ImageNet 사전학습 가중치를 사용합니다. 최초 약 45MB 다운로드와 다음 실행을 위한 캐시가 필요합니다. 수업 전에 교사가 준비하세요.

```powershell
python -c "from torchvision.models import resnet18, ResNet18_Weights; resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)"
python -c "import torch; print(torch.hub.get_dir())"
```

오프라인 PC에는 **공식 사이트에서 받은** `resnet18-f37072fd.pth`를 출력된 hub 폴더의 `checkpoints` 안에 복사합니다. 가중치 파일은 이 ZIP에 넣지 않았습니다. 교사용 `운영/prepare_weights.py`로 다운로드·해시·전처리를 점검할 수 있습니다.

**이번 제작 환경에서는 공식 가중치 다운로드가 차단되어 실제 사전학습 모델의 학습·성능을 실행 검증하지 못했습니다.** 전이학습 파일에 임의의 정확도를 예상값으로 넣지 않았습니다. 무작위 가중치로 수행한 테스트는 동결·파라미터 그룹·BN 상태의 구조 검사일 뿐 전이학습 성능 검증이 아닙니다.

`weights=None`으로 바꿔 실행한 결과를 전이학습 결과로 제출하지 않습니다. 가중치를 준비하지 못했다면 해당 실습은 **미실행**으로 기록하고 교사 시연으로 동결 범위·파라미터 수를 확인합니다. 다른 실습은 독립적으로 진행할 수 있습니다.

## 01_tensor.py · 이미지 Tensor

PPT 12쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 01_tensor.py
```

### 직접 완성할 부분

- **B01**: RGB 이미지 4장, 높이·너비 32인 Tensor를 만든다. 힌트: 첫 크기를 4로 수정한다.

### 확인할 결과

```text
shape: (4, 3, 32, 32)
dtype: torch.float32
device: cpu
첫 이미지: (3, 32, 32)
```

**완료·설명**: N/C/H/W를 자기 말로 설명하고 같은 값을 다른 축 순서로 표시한 것과 이미지 내용이 변한 것을 구분합니다.
1. N/C/H/W
N: Batch Size(배치 크기): 한 번에 모델에 입력되는 이미지의 개수
C: Channel(채널 수): 이미지를 구성하는 색상 정보의 수(3은 RGB -> 컬러이미지, 1은 흑백이미지)
H: Height(세로 높이): 이미지의 세로 방향 픽셀 수
W: Width(가로 높이): 이미지의 가로 방향 픽셀 수
PyTorch는 기본적으로 이미지 데이터를 처리할 때[N, C, H, W] 순서를 표준으로 사용합니다.

2. 딥러닝 프레임워크나 라이브러리에 따라 이 차원의 순서가 다를 수 있습니다.
포맷(순서)            | 주로 사용 하는곳                 |설명
NCHW(Channels-First) | PyTorch                        | 각 채널(R,G,B)의 2차원 평면 전체를 메모리에 차례대로 일렬로 나열하는 방식입니다.(예: R 평면 다 채우고 그 다음 G 평면, 그다음 B 평면)
NHWC(Channels-Last)  | TensorFlow, OpenCV, Matplotlib | 한 픽셀 위치 안에 있는 채널 정보를 묶어 메모리에 저장하는 방식입니다.(예: (0,0) 위치의 R,G,B 값을 저장한 뒤, (0,1) 위치의 R,G,B 값을 순서대로 저장)

데이터 순서 변환 방법(PyTorch): images.permute(0,2,3,1) 명령어를 사용하면 [4,3,32,32] 크기의 NCHW텐서를 [4,32,32,3] 크기의 NHWC 텐서로 축의 순서만 바꿀 수 있습니다.

3. 축의 순서를 바꾸는 작업(permute나 view 등)을 할 때, 데이터를 어떻게 다루느냐에 따라 이미지 내용이 완전히 망가질 수도 있고 안전하게 형태만 바뀔 수도 있습니다.
1) 축의 순서만 정상적으로 바뀐 경우(permute, transpose)
메모리 내부 원소들의 상대적 위치와 논리적 구조를 유지한 채 차원의 축 번호만 재배치하는 방식입니다.
데이터가 깨지지 않으므로, 축의 순서가 [4,32,32,3](NHWC)으로 바뀌어도 시각화 라이브러리(matplotlib.pyplot.imshow) 등을 통해 원래 형태의 이미지 내용을 정상적으로 볼 수 있습니다.
2) 이미지 내용이완전히 변하고 깨지는 경우(viw, reshape를 잘못 쓴 경우)
파이토치에서 차원 크기를 강제로 바꾸기 위해 images.view(4, 32, 32, 3) 같은 명령어를 잘못 쓰면 이미지 내용이 완전히 뭉개지고 변해버립니다.
.view() 함수는 메모리에 저장된 데이터의 실제 순서(1열로 쭉 나열된 상태)는 건드리지 않고, 사람이 읽는 방의 크기(차원 틀)만 강제로 늘이거나 줄입니다.
NCHW 형태로 나열되어 있던 메모리 데이터를 강제로 NHWC 구조의 틀에 끼워 맞추다 보니, 전혀 다른 위치의 픽셀 값과 채널 값이 섞이게 되어 원래 이미지의 형체를 알아볼 수 없는 노이즈 이미지로 변하게 됩니다.

차원의 순서만 다른 축(예: NHWC)으로 올바르게 표현하려면 데이터 흐름을 유지해 주는 permute를 사용해야 하며, 단순 차원 변형인 view를 잘못 쓰면 데이터 순서가 꼬여 이미지 내용이 오염됩니다.

## 02_conv.py · 합성곱

PPT 22쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 02_conv.py
```

### 직접 완성할 부분

- **B02**: 3입력·8출력·3×3·padding 1의 합성곱 층을 만든다. 힌트: 선택 인자 padding=1을 추가한다.

### 확인할 결과

```text
입력: (4, 3, 32, 32)
출력: (4, 8, 32, 32)
파라미터: 224
```

**완료·설명**: 입력·출력의 공간 크기와 학습 파라미터 수를 계산하고, stride가 바뀌어도 파라미터 수가 그대로일 수 있는 이유를 설명합니다.

## 03_pool.py · Pooling과 CNN

PPT 34쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 03_pool.py
```

### 직접 완성할 부분

- **B03**: 출력 높이·너비를 절반으로 만드는 MaxPool을 작성한다. 힌트: 커널 크기를 2로 바꾼다.

### 확인할 결과

```text
Conv2d (4, 16, 32, 32)
ReLU (4, 16, 32, 32)
MaxPool2d (4, 16, 16, 16)
Conv2d (4, 32, 16, 16)
ReLU (4, 32, 16, 16)
MaxPool2d (4, 32, 8, 8)
AdaptiveAvgPool2d (4, 32, 1, 1)
Flatten (4, 32)
Linear (4, 2)
```

**완료·설명**: Conv/Pool/Adaptive Pool/Flatten/Head를 거치는 shape를 적고, 마지막 출력 2개가 클래스 점수라는 것을 설명합니다.



## 04_images.py · 이미지 읽기

PPT 47쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 04_images.py
```

### 직접 완성할 부분

- **B04**: data/train을 주어진 transform으로 읽는다. 힌트: transform=transform을 전달해야 Tensor 배치를 만들 수 있다.

### 확인할 결과

```text
학습 이미지: 12
클래스: {'horizontal': 0, 'vertical': 1}
배치: (4, 3, 32, 32) (4,)
라벨: [0, 0, 0, 0]
```

**완료·설명**: `class_to_idx`에서 0·1의 의미를 확인합니다. train과 valid가 같은 클래스 순서를 사용하고, valid에서 무작위 변환이 없는 이유를 설명합니다.

1. 출력된 {'horizontal':0, 'vertical':1}은 폴더명을 기준으로 파이토치가 Target(정답) 데이터를 숫자로 매핑한 결과입니다.

0의 의미: 이미지가 horizontal(가로) 폴더에서 나왔음을 의미합니다.
1의 의미: 이미지가 vertical(세로) 폴더에서 나왔음을 의미합니다.

ImageFolder는 하위 폴더의 이름을 알파벳 순서(Alphabetical order)로 정렬합니다. h가 v보다 알파벳 순서상 앞에 있기 때문에 horizontal이 0번, vertical이 1번 클래스로 컴퓨터가 이해할 수 있는 정수형 라벨이 된 것입니다.

첫 번째 배치의 라벨이 [0, 0, 0, 0]인 이유는 데이터를 섞지 않았기(shuffle=False)때문에 0번 폴더(horizontal)의 이미지 4장이 순서대로 나왔기 때문입니다.

2. train(모델을 학습하는 폴더)과 valid(검증하는 폴더)의 일치성은 모델의 성능 측정과 직결됩니다.

만약 train 데이터셋은 가로를 0, 세로를 1로 학습했는데 valid 데이터 셋을 만들 때 폴더 구조나 정렬이 꼬여 가로가 1, 세로가 0이 된다면 모델은 학습한 대로 가로 이미지에 대해 0이라는 올바른 예측을 내놓았음에도 검증 세트의 정답지(1)와는 다르다는 이유로 오답 처리가 됩니다.

모델이 아무리 똑똑하게 학습되어도 검증 정확도(validation Accuracy)가 0% 가깝게 나옵니다.

이런 경우, 파이토치의 ImageFolder를 사용하고 두 폴더의 하위 폴더명(horizontal, vertical)을 통일해주면, 동일하게 알파벳 순서로 정렬되므로 두 데이터 셋의 클래스 순서가 항상 똑같이 유지되어 안전합니다.

3. transforms.Compose를 정의할 때, 학습 세트에는이미지 리사이즈 외에도 RandomHorizontalFlip(무작위로 뒤집거나), RandomRotation(무작위로 회전) 등의 데이터 증강(Data Augmentation) 기법을 자주 사용합니다. 하지만 valid(검증)나 Test(테스트) 세트에는 이를 절대 사용하지 않고 Resize와 ToTensor 같은 최소한의 고정 변환만 적용해야 합니다.

검증 세트의 목적은 "현재 모델의 순수한 예측 실력이 어느 정도인가?"를 평가하는 것입니다. 만약 검증 세트의 이미지를 무작위로 회전하거나 비틀면, 원본 이미지의 특징이 왜곡되어 모델이 원래 맞출 수 있던문제도 틀릴 수 있습니다. 지금 데이터처럼 horizontal과 vertical을 맞추는 문제에서 RandomRotation을 검증 데이터에 넣어버리면 가로이미지가 세로로 돌아가버리는 정답 자체가 바뀌는 치명적인 오염이 발생합니다.

검증 데이터가 매번 실행할 때마다 무작위로 변하면, 모델의 실력이 좋아져 검증 점수가 오른건지 운 좋게 쉬운 변형이 걸려 점수가 오른 것인지 구분할 수 없습니다. 따라서 검증 데이터는 항상 고정된 형태로 Benchmark(고정 점수) 역할을 해야 합니다.

## 05_train.py · CNN 학습과 Best

PPT 58쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 05_train.py
```

### 직접 완성할 부분

- **B05**: loss를 역전파하고 optimizer로 한 번 갱신한다. 힌트: loss.backward() 다음 optimizer.step().

### 확인할 결과

```text
epoch=1 train_loss=0.6703 valid_loss=0.6718 valid_acc=0.50
epoch=2 train_loss=0.6389 valid_loss=0.6442 valid_acc=0.50
epoch=3 train_loss=0.5896 valid_loss=0.6020 valid_acc=1.00
epoch=4 train_loss=0.5209 valid_loss=0.5423 valid_acc=1.00
epoch=5 train_loss=0.4358 valid_loss=0.4664 valid_acc=1.00
선택한 epoch: 5
```

**완료·설명**: valid loss가 최소인 epoch를 찾고 마지막 모델과 best 모델의 차이를 설명합니다. 정답이 높아도 간단한 합성 이미지의 소표본 결과임을 함께 적습니다.

## 06_transfer.py · 실제 전이학습

PPT 70쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 06_transfer.py
```

실제 사전학습 가중치가 필요합니다. 위 사전 준비를 먼저 확인합니다. 제작 환경의 실제 전이학습 실행 결과는 **미검증**입니다. 파라미터 수 1026(Head-only)과 입력 `[B,3,224,224]`를 먼저 확인하고 정확도는 본인 환경에서 기록합니다.

### 직접 완성할 부분

- **B06**: 기존 parameter의 requires_grad를 False로 설정한다. 힌트: 새 fc를 만들기 전에 Backbone의 미분을 끈다.

### 확인할 결과


**완료·설명**: `requires_grad=False`가 BN의 running 통계를 자동 고정하지 않는 이유를 설명합니다. `eval()`은 gradient 계산 자체를 끄지 않으므로 fc는 학습할 수 있습니다.



## 07_benchmark.py · CPU 시간 측정

PPT 81쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 07_benchmark.py
```

### 직접 완성할 부분

- **B07**: 처리한 이미지 수를 경과 초로 나눠 images/s를 구한다. 힌트: seen / seconds

### 확인할 결과

`seconds > 0`, `images_per_second = images / seconds`입니다. CPU VRAM은 빈 값/N/A입니다. 정상 이미지가 한 epoch에 한 번씩 처리되는지 확인합니다. CPU-only 환경에서 GPU 결과를 0으로 채우지 않습니다. 실제 시간은 예상 숫자가 아닙니다.

**완료·설명**: 데이터 로딩 포함 여부·이미지 크기·배치·워밍업·장치·반복 수를 기록합니다. 서로 다른 측정 범위의 속도를 직접 비교하지 않습니다.

## 08_project.py · CNN 종합 프로젝트

PPT 87쪽과 연결합니다. 이 단계 폴더를 터미널의 현재 위치로 둡니다.

```powershell
python 08_project.py
```

### 직접 완성할 부분

- **B08**: model 순전파 후 정답과 CrossEntropyLoss를 계산한다. 힌트: loss_fn(logits, y_train)
- **B09**: 역전파 후 가중치를 갱신한다. 힌트: loss.backward(); optimizer.step()

### 확인할 결과

```text
epoch  train_loss  valid_loss  train_accuracy  valid_accuracy
     1      0.6703      0.6718             0.5             0.5
     2      0.6389      0.6442             0.5             0.5
     3      0.5896      0.6020             1.0             1.0
     4      0.5209      0.5423             1.0             1.0
     5      0.4358      0.4664             1.0             1.0
best epoch: 5 valid accuracy: 1.0
저장: history.csv, model_comparison.csv, valid_predictions.csv, best_model.pt
test 4장은 읽거나 모델에 전달하지 않았다.
```

**완료·설명**: `history`, `model_comparison`, 예측표와 best 가중치가 생성되는지 확인하고 3문장으로 결과와 한계를 설명합니다. **test는 보관합니다.**

## 마지막 기록(이 README에 직접 작성)

1. 오늘 학습한 입력/출력 shape: ______
2. 내 best epoch와 그때 valid loss·정확도: ______
3. SmallCNN과 ResNet18의 입력 크기·학습 범위 차이: ______
4. CPU 측정 범위와 GPU 미측정 여부: ______
5. 이 자료의 한계: 합성 이미지/표본 수/실제 사진과의 차이 ______

작은 정상 이미지에서 높은 정확도를 얻었더라도 실제 서비스 성능은 아닙니다. 구현과 설명을 평가하며 점수 자체를 높이려고 test를 보지 않습니다.
