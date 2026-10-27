"""실습 02: 깊이만 바꾸고 같은 train·valid에서 비교합니다."""
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
from sklearn.metrics import f1_score

for depth in [1, 3]:
    # TODO B02: 반복 중인 depth를 max_depth에 연결하세요.
    model = DecisionTreeClassifier(max_depth=depth, random_state=42) # 사이킷런이 제공하는 의사결정나무 분류 알고리즘 설계도(클래스) DecisionTreeClassifier()함수를 이용하여 input_chars를 바탕으로 failed(0 또는 1)를 이진 분류하는 역할을 맡습니다.
                                                                     # 나무가 아래로 뻗어나갈 수 있는 최대 층수(질문의 단계)를 'max_depth='로 값을 설정합니다.
                                                                     # 'depth=1' 단 한번의 질문만 던질 수 있는 가장 단순한 모델이 됩니다.(input_chasrs <= 500인가요? -> 끝)
                                                                     # 'depth=3' 첫 질문의 결과에 따라 최대 3단계까지 던져서 데이터를 총 2^n(3)개의 세부 영역으로 정밀하게 쪼갤 수 있는 더 복잡한 모델이 됩니다.
                                                                     # 의사결정나무는 데이터를 쪼갤 때 성능이 같은 최적의 질문 후보가 여러 개 존해하면 무작위로 선택하는 경우가 있습니다.
                                                                     # 난수 고정 시드를 지정해 두면, 언제 어디서든 항상 동일한 질문 규칙으로 나무를 만들도록 보장하여 실험의 일관성(재현성)을 지켜줍니다.
    # TODO 끝
    model.fit(X_train, y_train)
    train_f1 = f1_score(y_train, model.predict(X_train), zero_division=0)
    valid_f1 = f1_score(y_valid, model.predict(X_valid), zero_division=0)
    print(f"깊이 {depth}: train F1={train_f1:.3f}, valid F1={valid_f1:.3f}")
