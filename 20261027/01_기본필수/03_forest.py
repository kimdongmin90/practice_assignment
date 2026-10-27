"""실습 03: 여러 트리를 결합하는 Random Forest를 실행합니다."""
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

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

# 제공: 작은 숲 20개, 깊이 3. 오늘은 설정을 더 늘리지 않습니다.
model = RandomForestClassifier(n_estimators=20, max_depth=3, random_state=42, n_jobs=1)
# TODO B03: train으로 학습하고 valid를 예측하세요.
model.fit(X_train, y_train) # 전체 훈련 데이터(X_train, y_train)에서 중복을 허용하여 무작위로 샘플을 20번 쪼개어 복사본을 만드는 부트스트랩 샘플링을 합니다.
                            # 쪼개진 20개의 데이터셋에 대해 "max_depth=3" 제약 조건이 적용되어, 모든 나무는 최대 3단계의 질문까지만 가질 수 있도록 성장이 제한된 상태에서 각각 하나씩, 20개의 의사결정나무를 동시에 학습시킵니다.
                            # 각 나무가 학습한 고유의 질문 규칙과 결정 경계들이 model이라는 거대한 숲 객체 안에 일괄 저장됩니다.
prediction = model.predict(X_valid) # 학습이 완료된 model에 새로운 검증 데이터(X_valid)를 투입하면 민주적인 다수결 판정(Majority Voting)시스템이 돌아갑니다.
                                    # 검증 데이터(X_valid)가 들어오면, 20개의 의사결정나무가 각자의 규칙 대각선에 대입하여 0 또는 1이라는 의견을 독립적으로 냅니다.
                                    # 20개의 의견을 모아 투표를 진행합니다. 예를 들어 특정 행에 대해 14개 나무가 1이라 하고, 6개 나무가 0이라 하면 다수결 법칙에의해 최종 승자는 1이 됩니다. 
                                    # 모든 검증 데이터 행에 대해 집계된 최다 득표 라벨(0 또는 1)들이 배열 형태로 추출되어 prediction에 저장됩니다.
# TODO 끝
print("트리 수:", len(model.estimators_))
print("valid 예측:", prediction.tolist())
print("valid F1:", round(f1_score(y_valid, prediction, zero_division=0), 3))
