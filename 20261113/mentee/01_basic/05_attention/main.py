# 경로 설정 및 라이브러리 임포트
from pathlib import Path
import sys


# 전체 코드 접근 방식 (4대 핵심 설계)

# 1. 상위 폴더 모듈 임포트 경로 확보 (sys.path.insert)
# 	현재 실행 파일이 하위 폴더(예: 01_basic/02_attention)에 있어도 상위 폴더에 있는 공통 유틸리티(common/support.py)를 에러 없이 불러올 수 있도록 파이썬 시스템 경로를 동적으로 추가했습니다.
# 2. 헤드리스(Headless) 환경 시각화 설정 (matplotlib.use("Agg"))
# 	터미널이나 백엔드 서버처럼 그래픽 창(GUI)을 띄울 수 없는 환경에서도 그래프를 에러 없이 이미지 파일(.png)로 바로 저장하기 위해 백엔드를 "Agg"로 지정했습니다.
# 3. 실험 재현성 및 연산 안정성 확보 (manual_seed, set_num_threads)
# 	난수 시드(42)와 CPU 스레드 개수(1)를 고정하여 언제, 어느 컴퓨터에서 실행하더라도 100% 동일한 수치 결과가 나오도록 통제했습니다.
# 4. Self-Attention용 입력 텐서 준비 (q, k, v)
# 	3개의 토큰(시퀀스 길이 3)과 2차원 임베딩 벡터(차원 수 2)를 가진 입력 텐서 q를 만들고, 이를 복제(.clone())하여 자기 자신에게 집중하는 셀프 어텐션(Self-Attention) 입력을 완성했습니다.

HERE = Path(__file__).resolve().parent # 현재 파이썬 파일(__file__)의 절대 경로를 구한 뒤, 부모(HERE)와 조부모 폴더(LEVEL_ROOT) 위치를 추적합니다.
LEVEL_ROOT = HERE.parent
sys.path.insert(0, str(LEVEL_ROOT))  # 어느 작업 폴더에서 실행해도 common 패키지를 찾습니다.
                                     # 파이썬 모듈 검색 경로(sys.path)의 맨 앞(0번 인덱스)에 상위 폴더를 추가하여 common 모듈 인식 허용합니다.
import math
import torch
import matplotlib
matplotlib.use("Agg") # 모니터 화면 창을 띄우지 않고 백그라운드에서 .png(이미지 파일)만 바로 렌더링하여 저장하도록 설정합니다.
                      # 화면에 창을 띄우지 않고 파일 저장 전용으로 쓰기 위해 pyplot 임포트 전에 반드시 먼저 선언합니다.
import matplotlib.pyplot as plt
from common.support import write_json

# 재현성 고정 및 입력 데이터(Q, K, V) 초기화
torch.manual_seed(42) # 난수 발생 시드를 42로 고정하여 결과 재현성 보장합니다.
torch.set_num_threads(1) # 멀티스레딩으로 인한 미세한 부동소수점 연산 오차 및 병목 방지를 위해 단일 스레드(1)만 사용합니다.

def main():
    q=torch.tensor([[1.,0.],[0.,1.],[1.,1.]]) # 3개의 토큰이 각각 2차원 벡터값을 가지는 (3, 2) 크기의 실수형 텐서(Query) 생성합니다.
    k,v=q.clone(),q.clone() # 원본 텐서 q의 메모리 데이터를 독립적으로 복제(.clone())하여 Key(k), Value(v)에 할당합니디.

    # TODO D20-05-B01: Scaled Dot-Product Q@K.T/sqrt(d_k)로 (3,3) Score를 계산하세요.
    # 입력·대상: PPT Q/K/V 3×2 예제와 Bool Causal Mask를 사용합니다.
    # 완료 확인: outputs/attention_report.json의 masked weights=0, row_sums=1을 확인합니다.
    # 주의: Softmax 이전 scores와 이후 weights를 구분하고, 행=Query·열=Key로 표시합니다.
    # BEGIN D20-05-B01
    scores = q@k.T / math.sqrt(q.shape[-1])
    assert scores.shape==(3,3)
    # END D20-05-B01

    # TODO D20-05-B02: 미래 Key를 차단하는 upper-triangle Causal Mask를 작성하세요.
    # 입력·대상: PPT Q/K/V 3×2 예제와 Bool Causal Mask를 사용합니다.
    # 완료 확인: outputs/attention_report.json의 masked weights=0, row_sums=1을 확인합니다.
    # 주의: Softmax 이전 scores와 이후 weights를 구분하고, 행=Query·열=Key로 표시합니다.
    # BEGIN D20-05-B02
    mask = torch.triu(torch.ones(3, 3, dtype=torch.bool), diagonal=1)
    masked_scores = scores.masked_fill(mask, float("-inf"))
    # END D20-05-B02

    # TODO D20-05-B03: Score를 Softmax Weight로 바꾸고 Mask된 칸=0, 행 합=1을 확인하세요.
    # 입력·대상: PPT Q/K/V 3×2 예제와 Bool Causal Mask를 사용합니다.
    # 완료 확인: outputs/attention_report.json의 masked weights=0, row_sums=1을 확인합니다.
    # 주의: Softmax 이전 scores와 이후 weights를 구분하고, 행=Query·열=Key로 표시합니다.
    # BEGIN D20-05-B03
    weights = torch.softmax(masked_scores, dim=-1)
    row_sums = weights.sum(dim=-1)  # 각 Query 행의 합
    assert torch.allclose(row_sums, torch.ones(3), atol=1e-6)
    assert torch.all(weights[mask] == 0)
    # END D20-05-B03
    plain_weights=torch.empty(0)
    diff=None
    head_weights={}
    interpretation_limit=["Attention Weight만으로 모델의 최종 판단 전체를 설명할 수 없다"]

    # TODO D20-05-B04: Score·Causal Mask·Weight·행 합과 Output을 JSON으로 저장하세요.
    # 입력·대상: PPT Q/K/V 3×2 예제와 Bool Causal Mask를 사용합니다.
    # 완료 확인: outputs/attention_report.json의 masked weights=0, row_sums=1을 확인합니다.
    # 주의: Softmax 이전 scores와 이후 weights를 구분하고, 행=Query·열=Key로 표시합니다.
    # BEGIN D20-05-B04
    output = torch.zeros_like(v)  # TODO: weights @ v
    report = {
        "scores": [],        # TODO: scores.tolist()
        "causal_mask": [],   # TODO: mask.tolist()
        "weights": [],       # TODO: weights.tolist()
        "row_sums": [],      # TODO: row_sums.tolist()
        "output": [],        # TODO: output.tolist()
        "no_mask_weights": plain_weights.tolist(),
        "masked_vs_unmasked_l1": diff,
        "multi_head": head_weights,
        "limits": interpretation_limit,
    }
    write_json(HERE / "outputs" / "attention_report.json", report)
    raise NotImplementedError("D20-05-B04: TODO를 완성하세요")
    # END D20-05-B04

if __name__=="__main__":
    main()
