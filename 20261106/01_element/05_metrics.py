"""실습 05. 가상 기록 읽기. 이 표는 실제 모델 성능이 아닙니다."""
from pathlib import Path
import pandas as pd
BASE = Path(__file__).resolve().parent
history = pd.read_csv(BASE / "data/metrics_example.csv")
# >>> B06
# 요구: map50_95가 가장 큰 행을 선택하세요. idxmax는 첫 최대값의 index를 반환합니다.
best = history.loc[history["map50_95"].idxmax()] # history[""].idxmax() 함수로 map50_95 컬럼에서 가장 큰 값을 가진 첫 번째 행의 인덱스(Index Labels)를 찾아 변환합니다.
                                                 # history.loc[...] 명령어로 구한 인덱스를 기반으로 해당 행의 전체 데이터(에포크, 손실값, 평가지표 등)를 Pandas Series 형태로 뽑아냅니다.
# <<< B06
print("자료 종류: 읽기 연습용 가상 기록 — 실제 YOLO 성능 아님")
print("선택 epoch:", int(best["epoch"]))
print("mAP50:", best["map50"], "mAP50-95:", best["map50_95"])
print("mAP는 accuracy가 아닙니다. train이 아니라 valid의 위치·분류 평가 기록입니다.")
