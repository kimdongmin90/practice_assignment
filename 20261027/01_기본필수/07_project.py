"""실습 07~08: 분류 후보 2개를 비교하고 같은 파일을 다시 실행합니다."""
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

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.base import clone
from sklearn.metrics import f1_score

# 제공: 전날과 같은 입력 2열입니다. 실행시간과 failed는 입력에 넣지 않습니다.
features = ["input_chars", "task_type"]
X_train, X_valid = train[features], valid[features]
pre = ColumnTransformer([
    ("num", "passthrough", ["input_chars"]),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["task_type"]),
])
folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
candidates = [("Tree", DecisionTreeClassifier(max_depth=3, random_state=42)),
              ("Forest", RandomForestClassifier(n_estimators=20, max_depth=3, random_state=42, n_jobs=1))]
rows, cv_rows = [], []
predictions = valid[["request_id", "failed"]].copy()
for name, estimator in candidates:
    # 제공: 전처리까지 Pipeline에 포함하여 fold 학습 부분에서만 fit하게 합니다.
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO B07a: 전처리까지 연결한 model을 train에서 교차검증하세요.
    scores = cross_val_score(model, X_train, y_train, cv=folds, scoring="f1") # 모델의 "진짜 일반화 성능(체급)"을 측정하기 위해, 데이터를 3등분(n_splits=3)하여 릴레이 시험을 치릅니다.
                                                                              # 전체 12개의 훈련 데이터 중 8개로 pre(전치리)와 estimator(모델)를 동시 학습시키고, 남은 4개로 F1-Score를 채점합니다.
                                                                              # 이 과정을 3번 반복하며, 매번 사용된 파이프라인은 깨끗하게 리셋됩니다.
                                                                              # 3번의 시험 점수가 담긴 넘파이 배열 scores(예: array([0.333, 0.000, 0.667]))를 반환합니다.
    # TODO 끝
    # TODO B07b: 전체 train으로 학습하고 valid를 예측하세요.
    model.fit(X_train, y_train) # X_valid를 풀기 전에 X_train 데이터 12개 전체를 사용하여 최종 인공지능을 완성합니다.
                                # X_train을 받아 숫자형은 "passthrough", 문자형은 OneHotEncoder로 가공해 하나의 완성된 2차원 숫자 행렬을 생성합니다.
                                # 이 행렬과 y_train 정답지를 estimator(트리 또는 포레스트)에 매칭하여 최종 판단 기준선(가중치)을 생성하고 이를 파이프라인 내부에 고정 저장합니다.
    prediction = model.predict(X_valid) # 실전 학습이 완료된 완벽한 상태의 model 객체에 새로운 모의고사인 X_valid를 주입하여 최종 정답(0 또는 1)을 찍어냅니다.
                                        # X_valid가 파이프라인 첫 관문인 pre를 통과하고 훈련 때 사용했던 원-핫 인코딩의 카테고리 기준을 그대로 적용하여 데이터의 형태를 변환합니다.(handle_unknown="ignore" 옵션 덕분에 훈련 때 없던 새로운 task_type이 들어와도 에러 없이 0으로 처리하며 통과합니다.)
                                        # 변환된 데이터를 바탕으로 최종 학습된 규칙에 대입하여 각 행이 실패(1)인지 성공(0)인지 판정합니다.
                                        # 검증 데이터 4개에 대한 AI의 최종 판정 라벨 배열이 prediction 변수에 저장됩니다.
    # TODO 끝
    rows.append({"model": name, "CV_F1": scores.mean(),
                 "CV_std": scores.std(), "valid_F1": f1_score(y_valid, prediction, zero_division=0)})
    for number, value in enumerate(scores, start=1):
        cv_rows.append({"model": name, "fold": number, "F1": value})
    predictions[name] = prediction
    if name == "Forest":
        importance = pd.DataFrame({"feature": model["pre"].get_feature_names_out(),
                                   "importance": model["model"].feature_importances_})

# 제공: 입력 파일을 덮어쓰지 않고 결과 4개를 같은 폴더에 만듭니다.
comparison = pd.DataFrame(rows)
comparison.to_csv(HERE / "classification_comparison.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(cv_rows).to_csv(HERE / "cv_scores.csv", index=False, encoding="utf-8-sig")
predictions.to_csv(HERE / "validation_predictions.csv", index=False, encoding="utf-8-sig")
importance.to_csv(HERE / "feature_importance.csv", index=False, encoding="utf-8-sig")
print("분할:", len(train), len(valid), len(test))
print(comparison.round(3).to_string(index=False))
print("중요도")
print(importance.round(3).to_string(index=False))
print("저장: classification_comparison.csv, cv_scores.csv, validation_predictions.csv, feature_importance.csv")
print("test는 학습·변환·예측·평가하지 않았습니다.")
