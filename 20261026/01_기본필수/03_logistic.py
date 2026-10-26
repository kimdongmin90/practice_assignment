"""실습 03 기본필수: 작은 정상 자료로 확률과 클래스를 확인합니다."""
from sklearn.linear_model import LogisticRegression

# 원리 확인용 데이터입니다. X의 한 값은 작업 복잡도, y는 성공 0 / 실패 1입니다.
X = [[1], [2], [3], [4], [5], [6]]
y = [0, 0, 0, 1, 1, 1]
model = LogisticRegression()
# TODO B03: model을 X와 y로 학습하세요.
# 힌트: model.fit(입력, 정답)
model.fit(X, y) # 앞에서 선언한 로지스틱 회귀 모델(model)에게 X, y값을 사용ㅇ해 학습하고 fit()을 이용해서 학습을 시킵니다.
new = [[2], [5]]
print("클래스 순서:", model.classes_) # classes_(fit 처리한)와 model함수를 이용해서 확률 열의 라벨 순서를 정리합니다.
print("확률 [성공, 실패]:")
print(model.predict_proba(new).round(3)) # predict_proba 함수를 이용해 클래스별 확률을 예측합니다.
print("예측 클래스:", model.predict(new)) # predict 함수를 이용해 최종 클래스를 예측합니다.
# 이 작은 시연의 출력은 평가 점수가 아닙니다. 실제 성능 비교는 07번의 valid로 합니다.
