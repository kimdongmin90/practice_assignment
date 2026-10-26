"""실습 05 기본필수: train에서 정한 기준을 새 입력에도 적용합니다."""
from sklearn.preprocessing import StandardScaler

train = [[100], [200], [300]]
valid = [[400]]
scaler = StandardScaler() # 사이킷런(sklearn.preprocessing) 라이브러리가 제공하는 표준화 전처리도구의 설계도(클래스) StandardScaler() 함수를 이용합니다.
scaler.fit(train)  # 제공: 평균과 크기 기준은 train에서만 구합니다.
# TODO B05: valid를 transform하여 converted에 넣으세요.
# 힌트: 학습은 이미 끝났으므로 fit_transform이 아니라 transform을 씁니다.
converted = scaler.transform(valid) # 계산된 기준(valid)을 바탕으로 transform()함수를 이용하여 데이터를 변환하고 fit()함수를 이용하여 평균과 표준편차를 학습(계산)합니다.
                                    # valid 데이터는 fit_transform()이나 fit()을 다시 쓰면 안됩니다.
                                    # scaler 적용 후 coverted 데이터를 모델 예측(predict)에 그대로 투입해야 성능이 잘 나옵니다.
print("train 기준 평균:", scaler.mean_)
print("train 변환:", scaler.transform(train).round(3))
print("valid 변환:", converted.round(3))
print("변환 후 기준 평균:", scaler.mean_)
# valid에 다시 fit하지 않습니다. StandardScaler는 자료를 정규분포로 만들지 않습니다.
