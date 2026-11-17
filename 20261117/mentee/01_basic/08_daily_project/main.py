"""Day22 · AI 지식 답변 생성기 v2 | PPT 60~68 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded, daily_project
from coursekit.metrics import summarize_runs
from coursekit.records import table_rows

def project_cases():
    # TODO D22-08-B01: 최종 연동확인질문 H01·H02·H03을 같은 순서로 지정하세요.
    # 입력·완료 기준: 이미 본 질문이므로 새 holdout의 일반화성능이라고 부르지 않습니다.
    # BEGIN D22-08-B01
    cases = ["H01", "H02", "H03"] # 
    return cases # 
    # END D22-08-B01

def project_rows(runs):
    # TODO D22-08-B02: 각 실행의 상태·사용량·시간을 표행으로 연결하세요.
    # 입력·완료 기준: 실패한 행도 버리지 않습니다. 모든 질문의 예상답을 실측답으로 채우지 않습니다.
    # BEGIN D22-08-B02
    rows = table_rows(runs) # 
    return rows # 
    # END D22-08-B02

def project_summary(runs):
    # TODO D22-08-B03: 실제·모의·캐시·미실행을 분리하여 요약하세요.
    # 입력·완료 기준: 소수관찰로 P95·SLA·보편적모델 우열을 주장하지 않습니다.
    # BEGIN D22-08-B03
    summary = summarize_runs(runs) # 
    return summary  # 위 TODO와 raise 제거를 마친 뒤 반환합니다.
    # END D22-08-B03

def check_project(runs):
    # TODO D22-08-B04: 자동검사 후 사람 미평가 None을 유지하고 전송상한을 확인하세요.
    # 입력·완료 기준: 사람평가는 tools/review.py의 별도파일로 남깁니다. 새 API·DB·RAG는 만들지 않습니다.
    # BEGIN D22-08-B04
    for run in runs:
        assert run.get("evidence_ok") is None # 
        assert run.get("new_api_send_count", 0) <=4 # 
    # END D22-08-B04

def main():
    args=parse_args(HERE)
    runs=daily_project(args,prepare_cases=project_cases,make_table=project_rows,finish_summary=project_summary)
    if isinstance(runs,list):
        check_project(runs)

if __name__=="__main__":
    guarded(main)
