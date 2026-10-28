"""실습 07~08: 06번의 설정을 그대로 읽어 개발 16건으로 학습하고 test 4건을 최종 평가합니다."""
from pathlib import Path
import pandas as pd
import numpy as np
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
HERE = Path(__file__).resolve().parent
# 제공: 06번을 먼저 완료하세요. 이 프로그램은 CV·설정 선택을 다시 하지 않습니다.
plan = json.loads((HERE / "selection.json").read_text(encoding="utf-8"))
raw = pd.read_csv(HERE / "requests.csv").set_index("request_id")
develop = raw.loc[plan["train_ids"] + plan["valid_ids"]].copy()
test = raw.loc[plan["test_ids"]].copy()
# 제공: 행별 공식은 새 요청에도 동일하게 적용합니다. test로 통계나 설정을 학습하지 않습니다.
for table in (develop, test):
    table["log_input_chars"] = np.log1p(table["input_chars"])
model = DecisionTreeClassifier(max_depth=plan["max_depth"], random_state=plan["random_state"])
# TODO B07a: 개발 자료 16건의 선택된 입력과 failed로 학습하세요. test는 넣지 않습니다.
model.fit(develop[plan["features"]], develop["failed"]) # train과 valid 데이터가 통ㅇ합된 develop 데이터프레임 전체(12 + 4 = 16)를 학습 재료로 사용합니다.
                                                        # test 세트는 최종 평가를 위해 완전히 격리하고 학습에서 배제합니다.
                                                        # 하드코딩으로 특정 열 이름을 적는 대신, JSON 설정 파일에서 읽어온 변수 목록 plan["features"]를 인덱싱 괄호 안에 집어넣어 전처리 파이프라인의 유연성을 유지합니다.
                                                        # develop[...]를 통해 2차원 표 형태로 전달하고, failed 열은 1차원 벡터 형태로 매칭합니다.
# TODO 끝
# 0·1 두 클래스가 있는 정상 자료입니다. classes_에서 양성 1의 위치를 확인합니다.
positive_column = model.classes_.tolist().index(1)
# TODO B07b: test의 실패 확률을 구하세요. predict_proba의 positive_column 열만 선택합니다.
probability = model.predict_proba(test[plan["features"]])[:, positive_column] # develop[plan["feature"]] 구조를 사용하여 설계도에 선언된 변수들을 주입했으므로, 예측할 때도 정확히 쌍을 맞추어 test[plan["features"]]를 전달해야 에러가 나지 않습니다.(develop["features"] 부분은 오타로 판단하고 test[plan["features"]] 구조로 수정 적용합니다.)
                                                                              # 단순히 0이나 1로 정답을 찍어내는 .predict() 함수 대신, 내부의 미세한 수치적 확률(0.12, 0.85)을 얻기 위해 .predict_proba() 함수로 접근합니다.
                                                                              # predict_proba() 결과물은 [성공확률, 실패확률]이 나란히 들어있는 2차원 배열입니다.
                                                                              # 앞 줄에서 model.classes_.tolist().index(1) 코드가 실제 실패(1) 라벨이 몇번째 방(0번째 또는 1번째)에 있는지 숫자를 찾아서 positive_column 변수에 저장해 두었습니다.
                                                                              # 따라서 모든 행(:)에 대해 해당 숫자 위치인 [:, positive_column] 열만 슬라이싱 기법으로 뽑아내어 일차원 실패 확률 배열을 완성합니다.
# TODO 끝
prediction = (probability > plan["threshold"]).astype(int)
# TODO B07c: F1에는 0/1 예측값, AUC에는 실패 확률을 넣으세요.
f1 = f1_score(test["failed"], prediction) # "임계값(칼같이 자른 기준선)을 통과한 뒤 맞춘 개수"의 균형을 보는 지표로 세번째 인자 자리에 성공/실패가 딱 떨어지는 prediction(0 또는 1 형태) 변수를 짝지어 줍니다.
auc = roc_auc_score(test["failed"], probability) # "기준성과 상관없이 모델이 매긴 점수 자체의 순위 판별력"을 보는 지표로 미세한 수치 점수인 probability(연속형 확률 형태) 변수를 짝지어 줍니다.
                                                 # 개발과정이 끝난 뒤 실전 평가 단계로 실제 정답 칸에는 y_train, y_valid가 아닌 최종테스트 값인 test["failed"]를 지정해 줍니다.
# TODO 끝
metrics = {"n": len(test), "Accuracy": accuracy_score(test["failed"], prediction),
           "Precision": precision_score(test["failed"], prediction, zero_division=0),
           "Recall": recall_score(test["failed"], prediction, zero_division=0),
           "F1": f1, "ROC_AUC": auc, "TP": int(((test["failed"] == 1) & (prediction == 1)).sum()),
           "actual_failed": int(test["failed"].sum()), "threshold": plan["threshold"]}
result = pd.DataFrame({"request_id": test.index, "actual": test["failed"].to_numpy(),
                       "probability_failed": probability, "predicted": prediction})
result.to_csv(HERE / "test_predictions.csv", index=False, encoding="utf-8-sig")
(HERE / "test_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print("개발/최종평가:", len(develop), len(test))
print(result.round(3).to_string(index=False))
print("혼동행렬:", confusion_matrix(test["failed"], prediction, labels=[0, 1]).tolist())
print(f"Accuracy={metrics['Accuracy']:.3f}, Precision={metrics['Precision']:.3f}, Recall={metrics['Recall']:.3f}, F1={f1:.3f}, AUC={auc:.3f}")
print("저장: test_predictions.csv, test_metrics.json")
print("08번은 이 설정 그대로 재실행합니다. test를 보고 06번 설정을 다시 고르지 않습니다.")
