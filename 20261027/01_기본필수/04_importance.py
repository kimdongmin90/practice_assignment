"""실습 04: 정상 숫자 두 열의 중요도를 확인하는 작은 원리 예제입니다."""
from sklearn.ensemble import RandomForestClassifier

# 각 행은 [글자 수, 허용 도구 수]입니다. 별도 원리 예제이며 requests.csv와 다른 자료입니다.
X = [[100, 1], [200, 2], [300, 1], [700, 2], [800, 1], [900, 2]]
y = [0, 0, 0, 1, 1, 1]
names = ["글자 수", "허용 도구 수"]
model = RandomForestClassifier(n_estimators=20, max_depth=2, random_state=42, n_jobs=1)
model.fit(X, y)
# TODO B04: 학습한 model의 feature_importances_를 읽으세요.
importance = model.feature_importances_ # 20개의 n_estimators=20(의사결정나무)가 서로 다른 기준과 무작위 샘플로 열심히 학습을 마친 랜덤 포레스트 인스턴스입니다.
                                        # 사이킷런의 규칙에 따라 fit(학습)이 끝난 모델에만 우측 하단에 _가 붙은 고유 속성이 생성된 feature_importances_에 각 변수가 노드를 분할할 때 불순도(Gini Impurity)를 얼마나 많이 감소시켰는지 감소량을 모두 더한 뒤, 전체 변수의 기여도 합이 1.0(100%)이 되도록 정규화(비율 변환)한 값입니다.
                                        # 추출된 결과가 넘파이 배열([값1, 값2]) 형태로 importance에 저장됩니다.
# TODO 끝
for name, value in zip(names, importance):
    print(f"{name}: {value:.3f}")
print("중요도가 높아도 실패의 원인이라고 단정하지 않습니다.")
