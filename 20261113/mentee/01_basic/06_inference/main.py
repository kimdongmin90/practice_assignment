# 코드 접근 방식 (3대 핵심 설계)

# 1. 로짓(Logits)의 확률 분포 변환 (torch.softmax)
# 	모델이 출력한 날것의 점수(logits = [2.0, 1.0, 0.0])에 소프트맥스를 적용하여, 모든 항목이 0과 1 사이의 값을 가지며 전체 합이 1.0이 되는 확률 분포로 변환합니다.
# 2. 수치 무결성 자가 검증 (assert torch.isclose)
# 	부동소수점 계산 오차(1e-6)를 허용하는 범위 내에서 확률의 총합(prob.sum())이 정확히 1.0이 되는지 코드 실행 중 스스로 검증합니다.
# 3. 온도(Temperature) 스케일링 비교 실험 (for temperature in ...)
# 	로짓을 온도값(\(T\))으로 나눈 뒤 소프트맥스를 적용(\(\text{softmax}(\text{logits} / T)\))하여, 온도가 낮을 때(\(0.5\))는 1등 확률이 더 뾰족하게 커지고(보수적/결정적), 온도가 높을 때(\(2.0\))는 확률이 평평하게 퍼지는(창의적/다양성) 현상을 비교 기록합니다.

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent # 상위 폴더의 공통 유틸리티(common/support.py)를 불러오기 위해 파이썬 모듈 경로에 조부모 폴더를 추가합니다.
LEVEL_ROOT = HERE.parent
sys.path.insert(0, str(LEVEL_ROOT))  # 어느 작업 폴더에서 실행해도 common 패키지를 찾습니다.
import torch
import torch.nn.functional as F
from common.support import write_json

torch.manual_seed(42) # 언제 실행해도 동일한 결과가 나오도록 난수 시드와 단일 스레드 환경 고정합니다.
torch.set_num_threads(1)

def main():
    logits=torch.tensor([2.0,1.0,0.0]) # 모델이 계산한 각 후보별 원시 점수 텐서(가장 큰 2.0이 유력한 후보)입니다.
    labels=["출력A","출력B","출력C"]

    # TODO D20-06-B01: Logit[2,1,0]을 Softmax로 바꾸어 확률의 합이 1인지 확인하세요.
    # 입력·대상: PPT의 예시 Logit [2,1,0]을 사용합니다.
    # 완료 확인: outputs/inference_report.json의 확률합=1과 T별 확률 변화·후보를 확인합니다.
    # 주의: Logit은 확률이 아니며 학습과 추론에서 parameter 변화 여부가 다릅니다.
    # BEGIN D20-06-B01
    prob = torch.softmax(logits, dim=0) # 0번 차원(dim=0) 기준으로 소프트맥스 함수를 적용해 확률값 계산합니다.
    assert torch.isclose(prob.sum(), torch.tensor(1.0), atol=1e-6) # 확률의 총합이 오차범위(1e-6) 이내에서 1.0과 일치하는지 확인(불일치 시 AssertionError 발생)합니다.
    # END D20-06-B01

    # TODO D20-06-B02: Temperature 0.5·1.0·2.0에서 확률 분포를 비교하세요.
    # 입력·대상: PPT의 예시 Logit [2,1,0]을 사용합니다.
    # 완료 확인: outputs/inference_report.json의 확률합=1과 T별 확률 변화·후보를 확인합니다.
    # 주의: Logit은 확률이 아니며 학습과 추론에서 parameter 변화 여부가 다릅니다.
    # BEGIN D20-06-B02
    temperature_results = {} # 온도 변화(0.5, 1.0, 2.0)에 따른 확률 분포 결과를 담을 딕셔너리 초기화합니다.
    for temperature in (0.5, 1.0, 2.0):
        temperature_results[str(temperature)] = []  # TODO: softmax(logits/temperature) 결과
    # END D20-06-B02

    # TODO D20-06-B03: Greedy로 다음 Token 후보를 선택하고 학습/추론 차이를 기록하세요.
    # 입력·대상: PPT의 예시 Logit [2,1,0]을 사용합니다.
    # 완료 확인: outputs/inference_report.json의 확률합=1과 T별 확률 변화·후보를 확인합니다.
    # 주의: Logit은 확률이 아니며 학습과 추론에서 parameter 변화 여부가 다릅니다.
    # BEGIN D20-06-B03
    selected_index = -1    # TODO: int(torch.argmax(prob).item())
    selected_token = ""     # TODO: labels[selected_index]
    training_vs_inference = {
        "training": "",       # TODO: loss·backward·파라미터 업데이트
        "inference": "",      # TODO: 가중치를 바꾸지 않고 다음 Token 예측
        "autoregressive": "", # TODO: 생성 Token을 다시 문맥에 추가
    }
    raise NotImplementedError("D20-06-B03: TODO를 완성하세요")
    # END D20-06-B03
    top_k={}
    sampled_index=None
    sampled_token=None
    top_p={}
    training_check={}
    kv_note={"stores":"이전 K/V 재사용","not":"학습이나 장기 기억이 아님"}

    # TODO D20-06-B04: 확률·선택·학습/추론 차이를 inference_report.json에 기록하세요.
    # 입력·대상: PPT의 예시 Logit [2,1,0]을 사용합니다.
    # 완료 확인: outputs/inference_report.json의 확률합=1과 T별 확률 변화·후보를 확인합니다.
    # 주의: Logit은 확률이 아니며 학습과 추론에서 parameter 변화 여부가 다릅니다.
    # BEGIN D20-06-B04
    report = {
        "logits": logits.tolist(),
        "probs": [],          # TODO: prob.tolist()
        "temperature": temperature_results,
        "greedy": {"index": selected_index, "token": selected_token},
        "sampling": {"index": sampled_index, "token": sampled_token},
        "top_k": top_k,
        "top_p": top_p,
        "training_vs_inference": training_vs_inference,
        "training_step": training_check,
        "kv_cache": kv_note,
    }
    write_json(HERE / "outputs" / "inference_report.json", report)
    raise NotImplementedError("D20-06-B04: TODO를 완성하세요")
    # END D20-06-B04

if __name__=="__main__":
    main()
