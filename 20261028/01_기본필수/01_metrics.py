"""실습 01: 실제 실패 6건인 손계산 예제입니다. 아직 모델을 학습하지 않습니다."""
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
# 행은 실제, 열은 예측입니다. 1은 좋은 결과가 아니라 관심 클래스인 '실패'입니다.
y = [0]*14 + [1]*6
pred = [0]*10 + [1]*4 + [0]*4 + [1]*2
print("혼동행렬(행 실제 / 열 예측, 성공0·실패1)")
print(confusion_matrix(y, pred, labels=[0, 1]))
# TODO B01: 네 지표 함수에 실제값 y와 예측값 pred를 순서대로 넣으세요. zero_division=0은 분모가 0일 때 0으로 표시하는 정책입니다.
acc = accuracy_score(y, pred) # 전체 데이터 중 맞춘 비율(성공, 실패 상관없이 맞춘 개수): 정확도
                              # (TN + TP) / 전체(TN + FN + FP + TP) = (10 + 2) / 20 =0.60
                              # 이 모델은 100건 중 60건의 성공/실패 여부를 정확히 맞춥니다.
precision = precision_score(y, pred, zero_division=0) # 모델이 실패(1)라고 예측한 것들 중, 실제 실패인 비율: 정밀도
                                     # TP / (TP + FP) = 2 / (2 + 4) = 2 / 6 = 0.333
                                     # 모델이 "요청 실패할 것 같다"라고 한 6건 중, 실제 실패는2건 뿐이므로 예측의 신뢰도가 33.3%라는 뜻입니다.(오탐/과잉진단을 줄여야 할 때 중요)
recall = recall_score(y, pred, zero_division=0) # 실제 실패(1) 데이터들 중에서, 모델이 놓치지 않고 찾아낸 비율: 재현율/민감도
                               # TP / (TP + FN) = 2 / (2 + 4) = 0.333
                               # 실제로 발생한 6건의 시스템 실패 중 AI가 2건만 찾아내고 4건은 놓쳤으므로 검출률이 33.3%라는 뜻입니다.(미탐/놓치는 것을 줄여야 하는 의료, 보안 분야에서 중요)
f1 = f1_score(y, pred, zero_division=0) # 정밀도와 재현율의 조화 평균(Harmonic Mean): F1-스코어
                       # 2 * ((정밀도 * 재현율) / (정밀도 + 재현율)) = 2 * ((0.333 * 0.333) / (0.333 + 0.333)) = 0.333
                       # 정밀도와 재현율 중 어느 한쪽으로 치우치치 않는 종합적인 균형 성적표입니다. 실패(1) 데이터를 잡는 능력이 정밀도와 재현율 모두 낮기 때문에 종합 점수인 F1-Score도 0.333이라는 낮은 수치를 기록하게 됩니다.
# TODO 끝
print(f"Accuracy={acc:.3f}, Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
print("실제 실패 6건 중 발견: 2건")
