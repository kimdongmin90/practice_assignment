# Day14 · 기본필수

**이 폴더의 README 하나로 01~08을 진행합니다.**

기본 결과는 소형 source Backbone 전이학습입니다. ImageNet ResNet18 성능이 아닙니다. 공식 ResNet18 경로는 최상위 README를 확인하세요.

## 파일 위치
Python 파일은 이 폴더에, 정상 입력은 `data/`에 있습니다. 결과는 이 폴더에 저장합니다.

VS Code로 이 폴더를 열고 터미널에서 아래 명령을 실행하세요. 파일의 위치를 기준으로 경로를 잡으므로 다른 작업 폴더에서도 절대 경로로 실행할 수 있습니다.

**TODO를 채우지 않은 코드는 실행돼도 정답이 아닙니다.** 출력·구현을 함께 확인하세요. 시험용 정상 입력만 사용하며 불량 파일 처리 과제는 없습니다.

## 공통 실험 약속
`train`만 학습에 사용하고, `valid`에서 epoch·후보를 비교합니다. test는 클래스 매핑·중복 감사 외에 모델 학습·추론·설명·임계값 선택에 사용하지 않습니다. valid는 자연적인 입력·분포를 유지하고 무작위 재추출하지 않습니다.
`head`: 새 Head만 학습합니다. `partial`: 마지막 Conv(상위 단계는 해당 BatchNorm affine 포함)+Head를 학습합니다. `requires_grad`와 BatchNorm의 running 통계는 별개이며 기본 정책은 BN 통계 고정입니다.
모든 작은 모델은 RGB float `[0,1]`, 32×32 입력입니다. ImageNet의 Resize256→CenterCrop224→Normalize 경로와 섞지 않습니다.
Grad-CAM은 선택한 logit에 대한 반응 지도이지 원인·정답·탐지 박스가 아닙니다. 입력 32×32 좌표의 열지도를 같은 좌표의 이미지에 합성합니다.
오답이 없으면 `오답 0건`이라고 쓰고 이미지를 억지로 만들지 않습니다. 05·06의 초기 모델과 07의 최종 모델 결과를 구분합니다. 낮은 성능도 정확히 실행·해석하면 정답입니다.


## 실습 01 · 데이터셋 구조·분할·불균형 · PPT 15쪽

열 파일: `01_dataset.py`. 직접 완성: B01

B01: ImageFolder로 train 폴더를 읽으세요. root는 필수 경로입니다.

```powershell
python 01_dataset.py
```

**사용 함수·인자**
`ImageFolder(root, transform=None)`: **root 필수**, 이미지 변환 transform은 선택. `.class_to_idx`는 클래스 이름→번호, `.targets`는 파일 순서와 같은 라벨 목록입니다. `.samples`를 보는 것은 학습이 아닙니다.

**확인 출력 — 제공 CPU 환경의 정답 실행**
```text
class_to_idx: {'circle': 0, 'square': 1, 'triangle': 2}
train 개수: [12, 6, 3] 같은 매핑: True
valid 개수: [3, 3, 3] 같은 매핑: True
test 개수: [2, 2, 2] 같은 매핑: True
```


**완료 기준**: TODO 구현, 위 수치·행 수·Shape와 대조, 생성 파일이 있다면 열어 확인.

**설명 질문**: 클래스 이름을 바꾸면 어떤 계약이 바뀌는가? train의 비율과 valid의 비율을 왜 따로 보는가?

내 설명: ______________________________


## 실습 02 · 사전학습 Backbone·새 Head · PPT 25쪽

열 파일: `02_head.py`. 직접 완성: B02

B02: 256개 특징에서 3개 logit을 출력하는 새 Linear Head를 만드세요.

```powershell
python 02_head.py
```

**사용 함수·인자**
`nn.Linear(in_features, out_features, bias=True)`: 입력·출력 수 **필수**, bias는 선택. `resnet18(*, weights=None, progress=True)`는 필수 위치 인자가 없으며 `weights`는 키워드 인자입니다. `np.load(file, allow_pickle=False)`는 배열 묶음을 읽는 제공 코드입니다. `.requires_grad`는 함수가 아니라 Parameter 속성입니다.

**확인 출력 — 제공 CPU 환경의 정답 실행**
```text
source 종류: 별도 합성 이미지로 사전학습한 TinyShapeCNN
학습 파라미터: 771
출력 shape: (2, 3)
ResNet18 구조 확인용 Head 파라미터: 1539
주의: 위 ResNet18은 구조만 확인했습니다. ImageNet 학습 결과가 아닙니다.
```


**완료 기준**: TODO 구현, 위 수치·행 수·Shape와 대조, 생성 파일이 있다면 열어 확인.

**설명 질문**: 고정 Backbone과 새 Head는 각각 무엇을 학습하는가? 공식 ResNet18과 소형 source의 출처는 같은가?

내 설명: ______________________________


## 실습 03 · Freeze·Partial Fine-tuning · PPT 35쪽

열 파일: `03_finetune.py`. 직접 완성: B03

B03: 두 전략에서 Head(9)를 열고, partial일 때 두 번째 Conv(4)도 여세요.

```powershell
python 03_finetune.py
```

**사용 함수·인자**
`AdamW(params, lr=..., weight_decay=...)`: **params 필수**, lr·weight_decay 선택. `zero_grad()`는 누적 기울기 초기화, `backward()`는 미분, `step()`은 실제 갱신입니다. `.eval()`은 gradient를 끄는 함수가 아닙니다.

**확인 출력 — 제공 CPU 환경의 정답 실행**
```text
strategy  trainable  valid_accuracy
    head        771             1.0
 partial       1923             1.0
```

숫자의 마지막 자릿수는 라이브러리·장치에 따라 달라질 수 있습니다. 시간은 정답으로 고정하지 않습니다.

**완료 기준**: TODO 구현, 위 수치·행 수·Shape와 대조, 생성 파일이 있다면 열어 확인.

**설명 질문**: requires_grad=False와 eval()은 어떤 점에서 다른가? partial은 어떤 층을 여는가?

내 설명: ______________________________


## 실습 04 · 클래스 불균형 대응 · PPT 47쪽

열 파일: `04_imbalance.py`. 직접 완성: B04

B04: f1_score에 average="macro", labels=[0,1,2], zero_division=0을 넣으세요.

```powershell
python 04_imbalance.py
```

**사용 함수·인자**
`f1_score(y_true, y_pred, average="macro", labels=[0,1,2], zero_division=0)`: 실제값·예측값 **필수**, 나머지는 선택 옵션. macro는 클래스별 F1의 동일 가중 평균입니다. `CrossEntropyLoss(weight=...)`는 train 손실에만 클래스 가중치를 적용합니다.

**확인 출력 — 제공 CPU 환경의 정답 실행**
```text
클래스 수: [12, 6, 3]
Accuracy: 0.5714
Macro F1: 0.2424
              precision    recall  f1-score   support

      circle      0.571     1.000     0.727        12
      square      0.000     0.000     0.000         6
    triangle      0.000     0.000     0.000         3

    accuracy                          0.571        21
   macro avg      0.190     0.333     0.242        21
weighted avg      0.327     0.571     0.416        21
```


**완료 기준**: TODO 구현, 위 수치·행 수·Shape와 대조, 생성 파일이 있다면 열어 확인.

**설명 질문**: Accuracy는 높고 minority Recall은 0일 수 있는가? weight와 sampler는 무엇을 각각 바꾸는가?

내 설명: 

1. 완벽하게 가능하며 불균형 데이터셋에서 흔하게 발생하는 대표적인 현상입니다.
이유는 정확도(Accuracy)의 계산 산식에 있는데 정확도는 전체 데이터 중 '맞춘 개수'만 중요하게 생각할 뿐, 그것이 어떤 클래스인지는 구분하지 않기 때문입니다.

1) 다수 클래스(Majority)의 지배력: 데이터셋 전체 21개 중 다수 클래스(circle)가 12개로 약 57%를 차지하고 있습니다. 만약 다수 클래스의 비중이 95%인 데이터셋이었다면, 모델이 아무 학습도 안 하고 0번으로 다 찍기만 해도 Accuracy는 95%라는 높은 수치가 나옵니다.

2) 소수 클래스(Minority)의 소외: 이때 모델은 소수 클래스인 1번과 2번을 단 한 개도 맞추지 못했습니다. 따라서 실제 1번, 2번 정답 중에서 모델이 맞춘 비율을 뜻하는 Minority Recall(재현율)은 정확히 0이 됩니다.

모델이 소수 데이터를 완전히 무시하고 가장 많이 나오는 안전한 정답(다수 클래스)만 선택하도록 편향(Bias)되었기 때문에 이러한 기형적인 수치가 도출되는 것입니다.

2. 위 문제를 해결하기 위해 모델에게 "소수 클래스를 틀리면 벌점을 더 크게 받는다"는 것을 인지시키거나(Loss Weight), 학습할 때 소수 데이터를 더 자주 보여주어야 합니다(Sampler).

1) Loss Weight(손실 함수 가중치 조절)
PyTorch의 nn.CrossEntropyLoss(weight=...) 인자에 클래스별 역수 비율로 계산된 가중치 텐서를 주입합니다. 데이터 개수가 적은 클래스일수록 큰 가중치를 부여합니다. 예를 들어 weight = torch.tensor([1.0, 2.0, 4.0]) 형태로 설정하면, 모델이 2번(triangle) 클래스를 틀렸을 때 0번을 틀렸을 때보다 4배 더 큰 벌점(Loss)을 받게 만듭니다. 벌점을 안 받으려고 모델은 소수 클래스 예측에 강제로 집중하게 됩니다.

2) Sampler(데이터 샘플러 조절)
DataLoader를 선언할 때, 무작위로 뽑는 기본 옵션 대신 WeightedRandomSampler를 생성하여 sampler 인자에 넣어줍니다. 이렇게 하면 원본 데이터셋에는 2번이 3개밖에 없더라도, 모델이 학습하는 1개의 미니 배치 안에는 0번, 1번, 2번 데이터가 거의 1:1:1에 가까운 균등한 비율로 주입되도록 물리적인 샘플링 환경을 바꾸어 줍니다.


## 실습 05 · 평가·오류 이미지 분석 · PPT 57쪽

열 파일: `05_errors.py`. 직접 완성: B05

B05: 실제 y_valid와 predictions로 혼동행렬을 만드세요. 행=실제, 열=예측.

```powershell
python 05_errors.py
```

**사용 함수·인자**
`confusion_matrix(y_true, y_pred, labels=[0,1,2])`: **실제값·예측값 필수**, labels는 선택이지만 이 수업에서는 순서 고정. 행=실제, 열=예측. `classification_report`의 target_names는 labels와 같은 순서입니다. 분모 0을 0으로 보고하는 정책을 명시합니다.

**확인 출력 — 제공 CPU 환경의 정답 실행**
```text
혼동행렬:
 [[3 0 0]
 [1 2 0]
 [3 0 0]]
              precision    recall  f1-score   support

      circle      0.429     1.000     0.600         3
      square      1.000     0.667     0.800         3
    triangle      0.000     0.000     0.000         3

    accuracy                          0.556         9
   macro avg      0.476     0.556     0.467         9
weighted avg      0.476     0.556     0.467         9

오답 개수: 4
square_002.png 실제: square 예측: circle
triangle_000.png 실제: triangle 예측: circle
triangle_001.png 실제: triangle 예측: circle
```


**완료 기준**: TODO 구현, 위 수치·행 수·Shape와 대조, 생성 파일이 있다면 열어 확인.

**설명 질문**: 오답 이미지 하나의 실제·예측·확률을 근거로 관찰과 가설을 나누어 적어라. 오답이 없을 때는 어떻게 보고하는가?

내 설명: ______________________________


## 실습 06 · Grad-CAM·편향 가설 · PPT 68쪽

열 파일: `06_gradcam.py`. 직접 완성: B06

B06: 채널 가중합에 relu()를 적용해 양의 반응만 남기세요.

```powershell
python 06_gradcam.py
```

**사용 함수·인자**
`torch.autograd.grad(outputs, inputs)`: 미분할 scalar·대상 Tensor **필수**. 입력을 수정하지 않고 gradient tuple을 반환합니다. `.mean(dim=(2,3), keepdim=True)`는 공간 평균. `cv2.addWeighted(src1, alpha, src2, beta, gamma)`는 앞의 다섯 인자 **필수**, 같은 좌표·크기의 BGR 이미지끼리 합성합니다.

**확인 출력 — 제공 CPU 환경의 정답 실행**
```text
correct circle_000.png target: circle CAM: (32, 32)
wrong square_002.png target: circle CAM: (32, 32)
```


**완료 기준**: TODO 구현, 위 수치·행 수·Shape와 대조, 생성 파일이 있다면 열어 확인.

**설명 질문**: Heatmap의 target은 무엇인가? 같은 이미지에서 target이 바뀌면 지도가 달라질 수 있는가?

내 설명: ______________________________


## 실습 07 · 전이학습 프로젝트 · PPT 78쪽

열 파일: `07_project.py`. 직접 완성: B07, B08, B09

B07: 역전파와 Optimizer 갱신을 수행하세요.
B08: 각 행의 가장 큰 logit 열을 예측 라벨로 고르세요.
B09: metrics를 UTF-8 JSON 문자열로 저장하세요. 아래 제공된 경로를 사용합니다.

```powershell
python 07_project.py
```

**사용 함수·인자**
`DataFrame.to_csv(path, index=False)`: 여기서는 출력 경로를 명시합니다. `torch.save(obj, path)`는 **저장 객체·경로 필수**. 복원할 때는 본인이 생성한 파일에만 `torch.load(..., weights_only=True)`를 사용합니다. 기본필수는 모델 파일 저장을 요구하지 않습니다.

**확인 출력 — 제공 CPU 환경의 정답 실행**
```text
{"accuracy": 1.0, "best_epoch": 8, "macro_f1": 1.0, "source": "synthetic_source_pretraining", "test_used": false, "valid_n": 9}
오답 수: 0 예측 행: 9 test 사용: False
```

숫자의 마지막 자릿수는 라이브러리·장치에 따라 달라질 수 있습니다. 시간은 정답으로 고정하지 않습니다.

**완료 기준**: TODO 구현, 위 수치·행 수·Shape와 대조, 생성 파일이 있다면 열어 확인.

**설명 질문**: 어떤 입력·설정·seed·매핑을 고정해야 재실행 결과를 비교할 수 있는가? test를 왜 남겨 두는가?

내 설명: 

# 딥러닝 실험 재현성 분석 및 평가 프로세스 보고서

본 문서는 검증(Validation) 및 오답 분석 코드를 실행한 결과(`Accuracy: 1.0`, `오답 수: 0`, `Valid N: 9`)를 바탕으로, 동일한 결과를 재현하기 위한 고정 조건과 최종 평가를 위해 테스트셋을 격리해야 하는 이유를 기술합니다.

---

## 1. 재실행 결과 비교를 위해 고정해야 할 요소

현재 검증 데이터 9개에 대해 오답이 0개인 완벽한 상태이므로, 차후 실험(모델 구조 변경, 데이터 추가 등)과 공정하게 비교하려면 다음 4가지 레이어를 반드시 고정해야 합니다.

### 1) 입력 데이터 고정 (Input Data & DataLoader)
* **검증 데이터셋(`X_valid`, `y_valid`) 구성:** 9개의 샘플이 어떤 데이터인지, 파일 경로와 라벨이 완벽하게 일치해야 합니다.
* **셔플(Shuffle) 비활성화:** 현재 코드는 오답 인덱스(`errors[0]`)를 활용해 Grad-CAM을 뽑아냅니다. 데이터가 로드되는 순서가 바뀌면 인덱스가 뒤죽박죽되어 엉뚱한 이미지의 히트맵을 그리게 되므로 반드시 `shuffle=False`로 설정해야 합니다.

### 2) 하이퍼파라미터 및 모델 설정 고정 (Configuration)
* **`best_epoch` 및 가중치 저장 조건:** 현재 결과는 8번째 에포크의 가중치(`best_state`) 기준입니다. 재실행 시 가중치를 저장하는 체크포인트 기준(예: 최저 Loss 기준인지, 최고 Accuracy 기준인지)을 통일해야 합니다.
* **모델 아키텍처 슬라이싱 인덱스:** Grad-CAM 코드에서 `model[:7]`(특징 추출기)과 `model[7:]`(분류기)로 레이어를 숫자로 쪼개고 있습니다. 모델 구조가 바뀌어 이 인덱스가 어긋나면 코드가 정상 작동하지 않으므로 레이어 구조와 레이어 인덱스를 고정해야 합니다.

### 3) 난수 시드 고정 (Random Seed)
학습 과정에서 가중치 초기화, 데이터 증강(Augmentation), 배치 구성 등에 무작위성이 개입하므로 아래와 같이 파이썬, 넘파이, 파이토치 전체의 시드를 하나로 묶어 고정해야 합니다.
```python
import os
import random
import numpy as np
import torch

def seed_everything(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

### 4) 클래스 매핑 고정 (Label Mapping)
* 혼동 행렬(Confusion Matrix)과 점수 계산 시 `labels=[0, 1, 2]`와 `valid.classes`를 직접 사용하고 있습니다. 
* 폴더 구조나 데이터셋 설정이 바뀌어 클래스 인덱스 매핑(`0: 클래스A, 1: 클래스B`)이 뒤바뀌지 않도록 명시적인 딕셔너리로 매핑을 고정해야 합니다.

---

## 2. 테스트셋(Test Set)을 따로 남겨두는 이유

메트릭 결과에 `test_used: false`라고 명시되어 있듯, 검증 단계에서 테스트셋을 사용하지 않고 철저히 아껴두어야 하는 이유는 **'모델의 진짜 일반화 성능(실전 실력) 측정'**과 **'데이터 누수(Data Leakage) 방지'** 때문입니다.

### 1) 검증셋(Validation Set)의 한계: 모의고사
* 현재 코드에서 사용한 `best_state`와 `best_epoch: 8`은 **검증셋 점수가 가장 잘 나오는 시점의 가중치를 사람이(또는 코드가) 선택한 것**입니다.
* 비록 모델이 검증셋을 직접 미분(Backpropagation)하여 가중치를 업데이트하지는 않았지만, **"검증셋에 유리한 가중치를 골라내는 과정"**에 검증셋이 관여했습니다.
* 즉, 모델과 실험자가 검증셋의 정답과 특성에 알게 모르게 과적합(Overfitting)되었을 확률이 존재합니다.

### 2) 테스트셋(Test Set)의 역할: 수능 시험
* **미지의 데이터 환경 재현:** 테스트셋은 가중치 선정, 하이퍼파라미터 튜닝 등 모델 개발의 모든 과정에 단 1%도 관여하지 않은 완전히 순수한 데이터여야 합니다.
* **객관적인 실력 증명:** 현재 검증 데이터 수(`valid_n: 9`)가 매우 적기 때문에 100% 성능이 쉽게 나왔을 수 있습니다. 모델이 실제 세상에 배포되었을 때도 잘 작동할지 사기 없이 검증하려면, 철저히 숨겨두었던 테스트셋으로 단 한 번만 채점해야 오차 없는 객체적 성능을 증명할 수 있습니다.


## 실습 08 · 같은 프로젝트 재현 (PPT 83쪽)
07번 파일을 다시 실행합니다. 원본 data가 바뀌지 않았는지, metrics·predictions의 행 순서·값이 같은지 확인합니다.
최종 모델에 오답이 없으면 05·06의 초기 모델 오류와 분리하여 보고합니다. 마지막에 없는 오류를 만들거나 라벨을 바꾸지 않습니다.

| 기록 | 직접 작성 |
|---|---|
| 사용 모델·source 출처 | |
| train/valid 클래스 개수 | |
| 학습 범위·BN 정책 | |
| 주 지표와 이유 | |
| 관찰한 오류·CAM target | |
| 재실행 확인·한계 1개 | |

**07 생성 파일**: `metrics.csv`, `predictions.csv`, `history.csv`, `confusion.csv`, `project_cam.png`, 실제 오답이 있으면 `project_error_*.png`. 기본필수는 `metrics.json`도 생성합니다. 응용의 비교표는 세 후보를 포함하며 `predictions.csv`는 마지막 head+weight 후보의 예측입니다.
**06 생성 파일**: 기본 `cam_correct.png`·`cam_wrong.png`(해당 사례가 있을 때), 응용 `target_0_cam.png`·`target_1_cam.png`.

## 자주 막히는 지점
- 파일을 못 찾는 경우: ZIP 안에서 실행하지 말고 전체 압축을 푼 뒤 실행합니다. data를 삭제하지 않습니다.
- 같은 파일이 실행되는데 출력이 다른 경우: TODO, seed, source 배열, split, mode를 순서대로 확인합니다.
- Grad-CAM이 전부 0인 경우: 그 target의 양의 가중 반응이 없을 수 있습니다. 무조건 예쁜 열지도로 바꾸지 않습니다.
- `eval()` 안에서도 미분은 가능하지만 `inference_mode()`에서는 Grad-CAM을 계산하지 않습니다.
- 공식 ResNet18을 실행할 때는 Weight 사전 준비가 별도 필요합니다. 소형 source 실습은 다운로드 없이 진행합니다.

## 환경 준비
전날 쓰던 가상환경을 그대로 사용합니다. VS Code에서 현재 난이도 폴더를 **폴더 열기**로 엽니다.
```powershell
python -c "import torch, torchvision, cv2; print(torch.__version__, torchvision.__version__, cv2.__version__)"
```
필요한 패키지는 `torch`, `torchvision`, `numpy`, `pandas`, `scikit-learn`, `opencv-python`, `Pillow`입니다.
`torch`·`torchvision`은 [PyTorch 공식 설치 선택기](https://pytorch.org/get-started/locally/)의 서로 호환되는 조합을 설치합니다. GPU용 설치를 CPU판으로 임의 덮어쓰지 않습니다.
나머지가 없을 때만 다음을 실행합니다.
```powershell
python -m pip install numpy pandas scikit-learn opencv-python Pillow
```
`opencv-python`과 `opencv-python-headless`를 동시에 새로 설치하지 않습니다. 이미 정상 import되면 재설치하지 않습니다.
검증 환경: Python 3.13.5, torch 2.10.0+cpu, torchvision 0.25.0+cpu, numpy 2.3.5, pandas 2.2.3, sklearn 1.8.0, OpenCV 4.13.0, Pillow 12.3.0, Linux. Windows·macOS와 실제 GPU는 미검증입니다.

## 공식 참고자료
- [Torchvision ResNet18: Weight와 transforms](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html)
- [PyTorch 전이학습 튜토리얼](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- [CrossEntropyLoss: 가중 평균의 분모](https://docs.pytorch.org/docs/2.10/generated/torch.nn.CrossEntropyLoss.html)
- [DataLoader·WeightedRandomSampler](https://docs.pytorch.org/docs/2.10/data.html)
- [Module: train/eval·requires_grad·hook](https://docs.pytorch.org/docs/2.10/generated/torch.nn.Module.html)
- [classification_report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html)
- [Grad-CAM 원 논문](https://arxiv.org/abs/1610.02391)
기술 문서의 최신 버전 표기와 아래 실제 검증 환경을 혼동하지 않습니다.
