"""실습 01: 입력을 질문으로 나누는 트리를 만듭니다. 성능 평가가 아닌 원리 예제입니다."""
from sklearn.tree import DecisionTreeClassifier

X = [[100], [200], [300], [700], [800], [900]]
y = [0, 0, 0, 1, 1, 1]  # 같은 순서의 정답: 성공 0, 실패 1
model = DecisionTreeClassifier(max_depth=1, random_state=42)
# TODO B01a: X와 y로 model을 학습하세요.
model.fit(X, y) # 내부적으로 불순도(Gini Impurity 또는 Entropy)를가장 낮출 수 있는 최적의 분기점(Threshold)을 수학적으로 계산합니다.
                # 300과 700 사이에 엄청난 간격이 있고 그 주위를 기정믕로 정답이 0에서 1로 변하는 것을 알게됩니다. 트리는 보통 중간값인 500정도를 기준으로 삼고 내부적으로 "X<=500인가요?"라는 단 하나의 질문(알고리즘)을 완성하고 학습을 마칩니다.(True 0으로 False 1로 분류)
# TODO 끝
# TODO B01b: 250과 850을 예측하여 prediction에 넣으세요.
prediction = model.predict([[250], [850]]) # 학습이 끝난 model에 새로운 데이터 [[250], [850]](2차원 배열 구조)을 집어넣으면 초고속으로 판정을 내립니다.
                                           # [250] 검사: "250<=500인가요?" -> True(판정: 0), [850] 검사: "850<=500인가요?" -> False(판정: 1)
                                           # prediction에는 각 질문 결과물인 array[0, 1]이 배열 형태로 담깁니다.
# TODO 끝
print("분기 기준:", model.tree_.threshold[0])
print("250·850 예측:", prediction.tolist())
