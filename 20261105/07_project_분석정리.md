# `07_project.py` 코드 흐름 & 이해 포인트

대상 파일: `01_기본필수/07_project.py`  
주제: **Source Backbone 동결 + Head만 Fine-tuning** 후, 검증·오답 저장·Grad-CAM까지 한 번에 돌리는 미니 프로젝트

---

## 1. 한 줄 요약

제공된 `source_backbone.npz`로 CNN Backbone을 채우고 **Head(마지막 Linear)만 학습**한 뒤, valid 성능·예측·혼동행렬·오답 이미지·CAM을 저장한다.  
`test` 데이터는 **절대 읽지 않는다.**

---

## 2. 전체 흐름 (위에서 아래로)

```
[설정] seed, 경로, transform
    ↓
[데이터] ImageFolder(train/valid) → 텐서 스택 (X, y)
    ↓
[모델] Sequential CNN 구성
    ↓
[가중치] source_backbone.npz 로드 → Backbone 고정, Head만 학습
    ↓
[학습] 8 epoch · Head만 AdamW · best valid_loss 저장
    ↓
[평가] best 가중치 복원 → logit → 예측 → metrics
    ↓
[저장] metrics/history/predictions/confusion CSV + JSON
    ↓
[설명] 오답 PNG + Grad-CAM overlay
```

---

## 3. 구간별 코드 구성

### ① 환경·경로·전처리 (1~20행)

| 항목 | 의미 |
|------|------|
| `torch.manual_seed(14)` | 재현성 |
| `BASE` / `DATA` / `OUT` | 스크립트 위치 기준 경로 |
| `transform` | `Resize(32,32)` + `ToTensor()` → **[0,1] RGB 32×32** |

**이해 포인트**
- ImageNet ResNet 전처리와 **섞지 말 것**. 이 모델은 교육용 32×32 source 가중치용이다.

---

### ② 데이터 로드 (22~27행)

```text
train/valid 폴더 → ImageFolder → 전체를 한 번에 스택
X_*: (N, 3, 32, 32)
y_*: (N,) long
```

**이해 포인트**
- `ImageFolder`는 **폴더명 = 클래스**로 라벨을 붙인다.
- 미니 데이터라 DataLoader 없이 **전체 배치**로 학습한다.
- **test는 사용하지 않음** (`test_used: False`).

---

### ③ 모델 구조 (29~33행)

`nn.Sequential` 인덱스와 역할:

| index | 레이어 | 역할 |
|------:|--------|------|
| 0~3 | Conv→BN→ReLU→MaxPool | 특징 추출 (공간 절반) |
| 4~6 | Conv→BN→ReLU | 더 깊은 특징 |
| 7 | AdaptiveAvgPool2d(4,4) | 고정 해상도 4×4 |
| 8 | Flatten | 벡터화 (16×4×4=**256**) |
| **9** | **Linear(256, 3)** | **3클래스 Head (학습 대상)** |

주석 기준: **0~8 = Backbone**, **9 = Head**.

---

### ④ Source 가중치 + Freeze (35~46행)

1. `source_backbone.npz`의 수치 배열을 `state_dict`에 덮어씀  
2. **모든 파라미터 `requires_grad=False`**  
3. **`model[9]`만 `requires_grad=True`**  
4. `model.eval()` → BatchNorm의 running 통계를 **고정** (train 모드로 갱신하지 않음)  
5. Optimizer는 **`model[9].parameters()`만** AdamW

**이해 포인트 (핵심 개념)**
- `requires_grad=False` → 역전파 때 그 가중치는 **갱신 안 됨**
- `eval()` → Dropout/BN **동작 모드** 제어 (학습 on/off와는 별개지만, 여기서는 BN 통계 보존 목적)
- 이게 **Transfer Learning / Linear Probe**에 가까운 패턴이다.

---

### ⑤ 학습 루프 (48~64행) — TODO **B07**

각 epoch:
1. `optimizer.zero_grad()`
2. train loss = `CrossEntropy(model(X_train), y_train)`
3. **(TODO)** `loss.backward()` → `optimizer.step()`
4. valid loss 계산 (`no_grad`)
5. valid loss가 최저면 `best_state` 저장

끝나면 `model.load_state_dict(best_state)`로 **best epoch 복원**.

**내가 작성할 것 (B07)**
```python
loss.backward()
optimizer.step()
```

**이해 포인트**
- `zero_grad` → `forward` → `loss` → `backward` → `step` 순서
- 왜 best만 남기는지: **과적합/흔들림**에 대비한 early-selection

---

### ⑥ 예측·지표 (65~75행) — TODO **B08**

1. best 모델로 valid logit
2. `softmax` → 확률(`probabilities`)
3. **(TODO)** 행마다 최대 logit 인덱스 = 예측 라벨
4. accuracy, macro F1 등 → `metrics.csv`, `history.csv`, `predictions.csv`

**내가 작성할 것 (B08)**
```python
predictions = logits.argmax(1)
# 또는: predictions = logits.argmax(dim=1)
```

**이해 포인트**
- logit ≠ 확률. 분류 결정은 보통 **argmax(logit)** 으로 충분
- confidence는 `probabilities.max(1)` (가장 큰 클래스 확률)

---

### ⑦ JSON 저장 (76~79행) — TODO **B09**

`metrics` dict를 UTF-8 JSON 문자열로 파일에 저장.

**내가 작성할 것 (B09)** 예시 형태:
```python
(OUT / "metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, sort_keys=True),
    encoding="utf-8",
)
```
(과제에서 지정한 경로명이 있으면 그 경로를 따를 것.)

**이해 포인트**
- `ensure_ascii=False` → 한글 깨짐 방지
- `sort_keys=True` → 키 정렬로 비교/채점 안정

---

### ⑧ 혼동행렬·오답 이미지 (80~86행)

- `confusion_matrix` → `confusion.csv`
- 틀린 샘플 최대 8장 → `project_error_XX.png` (OpenCV는 BGR이므로 RGB→BGR 변환)

---

### ⑨ Grad-CAM 유사 설명 (88~103행)

1. 오답 첫 장(없으면 0번)을 골라 `requires_grad=True`
2. `model[:7]` = feature map, `model[7:]` = pool+flatten+head
3. 예측 클래스 logit에 대해 feature로 `autograd.grad`
4. 채널별 평균 gradient로 가중 → ReLU → 32×32 upsample
5. JET colormap + 원본 overlay → `project_cam.png`

**이해 포인트**
- “모델이 **어디를 보고** 그 클래스를 골랐는지” 시각화
- hook 대신 Sequential 슬라이싱(`[:7]`, `[7:]`)으로 feature를 분리한 점이 교육용 포인트

---

## 4. 출력 파일 정리

| 파일 | 내용 |
|------|------|
| `metrics.csv` / `metrics.json` | accuracy, macro_f1, best_epoch 등 |
| `history.csv` | epoch별 valid_loss |
| `predictions.csv` | 파일명, 정답, 예측, confidence |
| `confusion.csv` | 클래스별 혼동행렬 |
| `project_error_*.png` | 오답 샘플 |
| `project_cam.png` | Grad-CAM overlay |

---

## 5. 꼭 이해하고 넘어가야 할 개념 체크리스트

### 데이터·전처리
- [ ] `ImageFolder` 폴더 구조 ↔ 클래스 인덱스
- [ ] `ToTensor()`가 [0,255] → [0,1] float로 바꾸는 것
- [ ] 왜 32×32이고 ImageNet 정규화를 안 쓰는지

### 모델·전이학습
- [ ] Backbone vs Head (`model[9]`)
- [ ] `requires_grad` vs `eval()` / `train()` 차이
- [ ] source 가중치를 로드한 뒤 **Head만** 학습하는 이유

### 학습 루프
- [ ] `zero_grad` → forward → loss → `backward` → `step`
- [ ] `CrossEntropyLoss` 입력: logit + 정수 라벨
- [ ] best valid_loss 체크포인트 복원

### 평가·저장
- [ ] `argmax`로 클래스 예측
- [ ] accuracy / macro F1 / confusion matrix 의미
- [ ] CSV vs JSON 저장 목적

### 설명 가능성
- [ ] Grad-CAM이 “어느 feature가 예측에 기여했는지”를 보여주는 흐름
- [ ] OpenCV 저장 시 RGB↔BGR

### 과제 TODO만 보면
| 코드 | 할 일 |
|------|--------|
| **B07** | `loss.backward()` + `optimizer.step()` |
| **B08** | `logits.argmax(1)` 로 예측 |
| **B09** | `metrics`를 UTF-8 JSON으로 `write_text` |

---

## 6. 학습할 때 추천 순서

1. 모델 인덱스(0~9)를 직접 세어 Backbone/Head 경계 확인  
2. freeze 코드 읽고 “왜 Head만 optimizer에 넣는지” 말로 설명  
3. B07 → B08 → B09 순서대로 채우기  
4. `history.csv`에서 valid_loss가 줄었는지 확인  
5. `project_cam.png`와 오답 PNG를 보며 “틀린 이유 후보”를 한 문장으로 적어보기  

---

## 7. 주의사항 (과제 의도)

- **test 폴더를 읽거나 학습에 쓰지 말 것**
- Source 가중치는 Target 이미지로 사전학습한 파일이 **아님** (주석 명시)
- Backbone은 학습 중에도 `eval()` 유지 → BN running mean/var를 건드리지 않음
