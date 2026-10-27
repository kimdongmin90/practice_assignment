"""실습 05: XGBoost도 같은 fit·predict 흐름으로 실행합니다."""
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

# 제공: 이 파일 옆의 정상 CSV 20건을 읽습니다. 현재 터미널 위치와 무관합니다.
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "requests.csv")
develop, test = train_test_split(raw, test_size=0.2, stratify=raw["failed"], random_state=42)
train, valid = train_test_split(develop, test_size=0.25, stratify=develop["failed"], random_state=42)
# test 4건은 보관만 합니다. 입력은 실행 전에 아는 글자 수입니다.
X_train = train[["input_chars"]]
X_valid = valid[["input_chars"]]
y_train = train["failed"]
y_valid = valid["failed"]

from xgboost import XGBClassifier
from sklearn.metrics import f1_score

# 제공: 학습 회차 80·깊이 2·보정 크기 0.05를 고정합니다. CPU로 실행합니다.
model = XGBClassifier(n_estimators=80, max_depth=2, learning_rate=0.05,
                      objective="binary:logistic", eval_metric="logloss",
                      tree_method="hist", random_state=42, n_jobs=1)
# TODO B05: train으로 학습하고 valid를 예측하세요.
model.fit(X_train, y_train) # X_train을 보고 아주 단순한 기준(max_depth=2 -> 제약에 맞는 질문 2개짜리 나무)으로 1차 분류 규칙을 만듭니다.(초기 모델이라 많이 틀립니다.)
                            # 1번 나무가 맞춘 것과 틀린 것의 오차(Gradient)를 계산합니다.
                            # eval_metric="logloss"(로그 손실) 함수를 기준으로 오차의 크기를 수치화합니다.
                            # 2번 나무는 원본 데이터가 아닌 1번 나무가 남긴 오차를 정답으로 두고 이를 줄이기 위해 학습합니다. learning_rate=0.05(학습률)가 적용되어, 2번 나무가 찾아낸 규칙을 100% 다 반영하지 않고 5%만큼만 미세하게 반영하여 조심스럽게업데이트합니다.(이 과정이 80번 나무까지 반복됩니다.)
                            # 가중치가 세부 조정된 80개의 오답노트 나무 결합체가 model에 완성됩니다.
prediction = model.predict(X_valid) # X_valid 샘플이 80개의 나무 규칙을 차례대로 통과하며 스코어(로그값)가 누적 합산됩니다.
                                    # 누적된 점수를 바탕으로 내부 시그모이드 함수를 거쳐 최종 실패(1)할 확률(0~1 사이 값)을 도출합니다.
                                    # 최종 확률이 0.5(50%)를 넘기면 1(실패), 넘지 못하면 0(성공)으로 최종 변환하여, 각 데이터 행의 판정 결과 배열을 prediction 변수에 담아줍니다.
# TODO 끝
print("valid 예측:", prediction.tolist())
print("valid F1:", round(f1_score(y_valid, prediction, zero_division=0), 3))
print("학습 목적: 실패 분류 / 확인 지표: F1")
