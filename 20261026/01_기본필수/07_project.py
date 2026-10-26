"""실습 07~08 기본필수: 같은 파일을 완성하고 다시 실행합니다."""
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

# 제공: 이 파일 옆의 CSV를 읽고, 전날과 같은 요청들을 12 / 4 / 4로 나눕니다.
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "requests.csv")
develop, test = train_test_split(raw, test_size=0.2, random_state=42, stratify=raw["failed"])
train, valid = train_test_split(develop, test_size=0.25, random_state=42, stratify=develop["failed"])
# test는 보관만 합니다. 학습·예측에 넣지 않습니다.

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.base import clone
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, f1_score

# 제공: 전날의 두 입력을 그대로 사용합니다. elapsed_ms와 failed는 정답이므로 입력에서 뺍니다.
features = ["input_chars", "task_type"]
X_train = train[features]
X_valid = valid[features]
pre = ColumnTransformer([
    ("num", StandardScaler(), ["input_chars"]),
    ("cat", OneHotEncoder(sparse_output=False), ["task_type"]),
])
# 제공: 아래 두 반복은 같은 구조입니다. 첫 번째는 숫자, 두 번째는 클래스 정답을 사용합니다.
regression_rows = []
classification_rows = []
result = valid[["request_id", "elapsed_ms", "failed"]].copy()
for name, estimator in [("Dummy", DummyRegressor()), ("Linear", LinearRegression())]:
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO B07a: 실행시간 elapsed_ms로 학습하고 X_valid를 예측하세요.
    # 힌트: model.fit(X_train, train["elapsed_ms"]) 다음 predict(X_valid)를 연결합니다.
    model.fit(X_train, train["elapsed_ms"]) # Pipeline 첫 변환기인 pre(ColumnTransforme)가 가동되어 X_train 안의 수치형 데이터의 평균과 표준편차를 구하고, 범주형 데이터를 0, 1로 인코딩 후 학습용 최적의 숫자 행렬로 Transform합니다.
                                            # Transform된 숫자 행렬과 우리가 정답으로 넘겨준 train["elapsed_ms"](실제 걸린 시간)를 estimator(더미 또는 선형 회귀)에게 전달합니다.
                                            # 모델은 두 데이터를 매칭해가며 패턴을 학습합니다.
                                            # 전처리 기준 정보와 최적의 회귀 가중치가 반영된 최종 인공지능 결합체 model이 완성됩니다.
    prediction = model.predict(X_valid) # X_valid의 평균과 표준편차를 새로 구하지 않고 fit 단계에서 X_train을 통해 기억해 둔 평균과 표준편차 기준을 그대로 가져와 X_valid를 transform합니다.
                                        # 변환되어 컴퓨터가 이해할 수 있게 된 검증 데이터를 estimator에 전달하면, 모델은 학습한 공식을 대입해 예측처리시간(ms)를 계산합니다.
    regression_rows.append({"model": name, "MAE_ms": mean_absolute_error(valid["elapsed_ms"], prediction)}) # prediction값과 valid["elapsed_ms"](정답)이 비교되어 MAE나 RMSE 같은 오차 점수로 계산됩니다.
    result[name + "_ms"] = prediction

for name, estimator in [("Dummy", DummyClassifier(strategy="most_frequent")),
                        ("Logistic", LogisticRegression(max_iter=1000))]:
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO B07b: 실패 여부 failed로 학습하고 X_valid를 예측하세요.
    # 힌트: 회귀와 같은 흐름이며 정답 열만 failed로 바뀝니다.
    model.fit(X_train, train["failed"]) # X_train의 변수들이 pre(ColumnTransformer)을 거치며 컴퓨터가 연산할 수 있는 숫자 행렬로 가공됩니다.(수치형은 표준화, 범주형은 원-핫 인코딩)
                                        # 가공된 숫자 행렬과 우리가 정답으로 넘겨준 train["failed"](0 또는 1) 데이터를 estimator(Dummy 또는 Logistic)에게 전달합니다.
                                        # LogisticRegression의 경우, input_chars와 task_type가 어떨 때 실패(1)할 확률이 높아지는지 수학적 기준선(결정 경계)을 계산하여 학습합니다.
                                        # 분류 기준 전처리 정보와 최적의 분류 방정식 가중치가 결합된 최종 AI 결합체 model이 완성됩니다.
    prediction = model.predict(X_valid) # X_vaild 데이터를 변환할 때, 훈련할 때 X_train으로 기억해 둔 평균, 표준편차 및 범주 카테고리 기준을 그대로 적용하여 껍데기만 바꿉니다.(데이터 누수 방지)
                                        # 변환이 완료된 데이터를 바탕으로 로지스틱 회귀 모델이 내부적으로 실패 확률을 계산합니다.
                                        # 실패 확률이 기본 임계값(0.5)를 넘기면 최종 예측 결과를 1(실패)로 판정합니다.
                                        # 검증 데이터 각 행에 대해 AI가 예측한 0(성공) 또는 1(실패)의 배열이 prediction에 담기게 됩니다.
                                        # 이 값은 추후 실제 정답 valid["failed"]와 비교되어 F1-score, 정확도(Accuracy), 오탐/미탐 지표로 계산됩니다.
    classification_rows.append({"model": name, "F1": f1_score(valid["failed"], prediction, zero_division=0)})
    result[name + "_failed"] = prediction

# 제공: 두 종류의 지표를 섞지 않고 별도 표로 저장합니다. 저장 코드는 수정하지 않아도 됩니다.
regression = pd.DataFrame(regression_rows)
classification = pd.DataFrame(classification_rows)
regression.to_csv(HERE / "regression_comparison.csv", index=False, encoding="utf-8-sig")
classification.to_csv(HERE / "classification_comparison.csv", index=False, encoding="utf-8-sig")
result.to_csv(HERE / "validation_predictions.csv", index=False, encoding="utf-8-sig")
print("분할:", len(train), len(valid), len(test))
print("회귀 비교 / 낮은 MAE가 좋음")
print(regression.round(3).to_string(index=False))
print("분류 비교 / 높은 F1이 좋음")
print(classification.round(3).to_string(index=False))
print("저장: regression_comparison.csv, classification_comparison.csv, validation_predictions.csv")
print("test는 학습·예측하지 않았습니다.")
