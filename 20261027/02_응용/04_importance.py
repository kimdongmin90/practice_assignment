"""실습 04 응용: 전처리 출력 이름 8개와 중요도를 대응시킵니다."""
from pathlib import Path
import pandas as pd

# 제공: 전날의 분할 소속뿐 아니라 position 순서까지 그대로 읽습니다.
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")
manifest = pd.read_csv(HERE / "data/split_manifest.csv")
train_ids = manifest.loc[manifest["split"] == "train"].sort_values("position")["request_id"]
valid_ids = manifest.loc[manifest["split"] == "valid"].sort_values("position")["request_id"]
train = raw.loc[train_ids]
valid = raw.loc[valid_ids]
FEATURES = ["input_chars", "allowed_tools", "task_type", "priority"]
X_train, X_valid = train[FEATURES], valid[FEATURES]
y_train, y_valid = train["failed"], valid["failed"]
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)
# test 20건의 입력·정답은 아래 모델에 전달하지 않습니다.
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import clone

# 제공: 전날 배운 결측 대체와 문자 변환입니다. 통계는 fit할 때만 배웁니다.
pre = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), FEATURES[:2]),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                      ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), FEATURES[2:]),
])
# 트리는 이 실습에서 표준화하지 않습니다. 각 후보·fold마다 새 전처리기를 학습합니다.

from sklearn.ensemble import RandomForestClassifier

model = Pipeline([("pre", clone(pre)), ("model", RandomForestClassifier(n_estimators=100, max_depth=4, min_samples_leaf=2,
                                    max_features="sqrt", random_state=42, n_jobs=1))])
model.fit(X_train, y_train)
# TODO A04: 전처리의 출력 이름과 Forest의 중요도를 가져오세요.
names = model["pre"].get_feature_names_out() # get_feature_names_out() 함수를 사용해서 전처리가 완료된 후 최종적으로 출력(Out)되는 변수들의 이름을 리스트(배열) 형태로 반환합니다.
                                             # 원본 변수가 input_chars와 원-핫 인코딩을 거친 task_type이었다면, ['num__input_chars', 'cat__task_typeA', 'cat__task_typeB'] 같은 가공된 이름들을 정확하게 뽑아내 줍니다.
                                             # model["pre"]을 통해 파이프라인 안에서 첫 번째로 등록된 ColumnTransformer(전처리 도구)를 선택합니다.
values = model["model"].feature_importances_ # "n_estimators=100"이 데이터를 분류하는 과정에서 각 변수가 기여한 상대적 중요도 비율(0~1 사이 값, 총합은 1)을 숫자로 담고 있는 고유 속성입니다.
                                             # 중요도 배열의 길이는 앞 단계에서 추출한 names의 길이와 완벽하게 일치합니다.
# TODO 끝
result = pd.DataFrame({"feature": names, "importance": values}).sort_values("importance", ascending=False)
result.to_csv(OUT / "04_importance.csv", index=False, encoding="utf-8-sig")
print("변환된 특성 수:", len(names))
print(result.round(4).to_string(index=False))
print("중요도는 원인이나 신규 데이터 성능을 보장하지 않습니다.")
