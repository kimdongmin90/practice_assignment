"""Day22 · 명시적 모델 선택 | PPT 53~59 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded
from coursekit.config import choose_model as checkpoint_choose
from coursekit.labs import routing_lab

def route(mode, models):
    # TODO D22-07-B01: fast·quality만 허용하고 실제모델과 선택이유를 반환하세요.
    # 입력·완료 기준: 알 수 없는 모드를 fast로 조용히 바꾸지 않습니다. quality권한 없으면 not_run입니다.
    # BEGIN D22-07-B01
    if mode not in {"fast", "quality"}: 
        raise ValueError("지원하지 않는 실행 모드") # 
    return checkpoint_choose(mode, models) # 
    # END D22-07-B01

def record_view(result):
    # TODO D22-07-B02: 어떤 모델이든 동일한 결과필드로 비교하세요.
    # 입력·완료 기준: 고가모델이 항상 더 좋다는 결론을 미리 넣지않습니다.
    # BEGIN D22-07-B02
    row = {key: result.get(key) for key in ("case_id", "source_mode", "model", "route_reason", "run_status",
              "answer_object", "evidence_ok", "usage", "request_ms", "estimated_usd")} # 
    return row # 
    # END D22-07-B02

def comparison_modes():
    # TODO D22-07-B03: 명시적비교에서만 fast·quality를 한번씩 선택하세요.
    # 입력·완료 기준: 기본 run은 한 모델만 호출합니다. compare는 계정권한·예산 확인 후 선택합니다.
    # BEGIN D22-07-B03
    modes = ["fast", "quality"]  # fast와 quality 각 한번, while fallback 금지
    return modes # 
    # END D22-07-B03

def main():
    args=parse_args(HERE)
    routing_lab(args,router=route,record_view=record_view,compare_modes=comparison_modes)

if __name__=="__main__":
    guarded(main)
