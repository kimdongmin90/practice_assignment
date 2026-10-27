"""실습 06: train 12건 안에서만 3-fold 교차검증합니다."""
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
from sklearn.model_selection import StratifiedKFold, cross_val_score

# 제공: 각 클래스 수를 고려해 기본필수는 3-fold입니다. valid4·test4는 넣지 않습니다.
folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
model = DecisionTreeClassifier(max_depth=3, random_state=42)
# TODO B06: model을 train에서 3-fold F1으로 평가하세요.
scores = cross_val_score(model, X_train, y_train, cv=folds, scoring="f1") # model: 평가 대상이 되는 학습 전 상태의 DecisionTreeClassifier 객체입니다.
                                                                          # X_train, y_train: 교차 검증의 재료가 되는 훈련 데이터셋입니다.
                                                                          # cv=folds: 핵심 분할 제어 장치로 앞서 정의한 StratifiedKFold(n_splits=3)에 따라, 데이터를 3등분(Fold1, Fold2, Fold3)으로 나누어 검증을 설계하라는 지시입니다.
                                                                          # folds의 지휘 아래 전체 데이터를 3개로 나눈 뒤 3번의 독립된 시험을 치릅니다.(3회차에 걸친 릴레이 학습 및 채점 시스템)
# TODO 끝
print("fold별 F1:", scores.round(3).tolist())
print("평균 F1:", round(scores.mean(), 3))
print("표준편차:", round(scores.std(), 3))
