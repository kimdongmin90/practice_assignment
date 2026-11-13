# 전체 코드 접근 방식 (4대 핵심 설계)

# 1. 다단계 규칙 기반 검증 파이프라인 (if ~ elif ~ else)
# 	LLM의 답변(CASES)을 순회하면서 1) 스키마 형식 오류(format) → 2) 근거/출처 누락(evidence) → 3) 원본 사실 불일치(factual_mismatch) 순서로 우선순위를 두어 문제 유형을 정확하게 분류했습니다.
# 	F01: 출처(K01)는 있으나 원본('개인 폴더')과 다르게 '공용 서버 폴더'라고 답해 **factual_mismatch**로 분류됩니다.
# 	F02: 응답 딕셔너리 자체에 "sources" 키가 누락되어 **format**으로 분류됩니다.
# 	F03: "sources" 키는 있지만 빈 리스트([])로 근거가 비어 있어 **evidence**로 분류됩니다.
# 2. 오류 유형별 정의(Taxonomy) 명확화 (explanations)
# 	분류된 오류 코드(format, evidence, factual_mismatch)가 무엇을 의미하는지 사람이 이해할 수 있는 정의를 매핑했습니다.
# 3. 완화 전략 및 거버넌스 규칙 구조화 (report)
# 	단순 탐지에서 그치지 않고 오류 유형별 완화 대책(mitigation), 추가 검증 절차(checks), 에이전트 주의 사례(agent_case), 신뢰 원칙(trust_rules)을 하나의 JSON 리포트로 묶어 체계화했습니다.
# 4. 이중 포맷 리포트 출력 (write_json, write_md)
# 	시스템 연동용 데이터(review.json)와 사람이 읽기 편한 문서(review.md)를 동시에 생성하도록 설계했습니다.

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent # 현재 파일의 부모 폴더(HERE)와 상위 레벨 폴더(LEVEL_ROOT)를 찾아 모듈 검색 경로에 추가합니다.
LEVEL_ROOT = HERE.parent
sys.path.insert(0, str(LEVEL_ROOT))  # 어느 작업 폴더에서 실행해도 common 패키지를 찾습니다.
from common.support import write_json, write_md # 프로젝트 공통 모듈에서 JSON 및 Markdown 저장 헬퍼 함수를 불러옵니다.

# 세 예시는 수업용으로 사람이 미리 설계한 사례입니다. 실제 자동 사실성 검사기가 아닙니다.
CASES = [
    {"id":"F01","question":"파일을 어디에 보관하나요?",
     "source":"실습 파일은 개인 폴더에 보관합니다.",
     "answer":"실습 파일은 공용 서버 폴더에 보관합니다.","sources":["K01"]},
    {"id":"F02","question":"서버는 어디에서 실행하나요?",
     "source":"프로젝트 폴더에서 서버를 실행합니다.",
     "answer":"프로젝트 폴더에서 서버를 실행합니다."},
    {"id":"F03","question":"질문할 때 무엇을 함께 적나요?",
     "source":"오류 메시지와 시도한 작업을 함께 적습니다.",
     "answer":"오류 메시지와 시도한 작업을 함께 적습니다.","sources":[]},
]

def main():

    # TODO D20-07-B01: 3개 답변에서 정해 둔 형태·근거·사실 불일치를 분류하세요.
    # 입력·대상: 제공된 F01/F02/F03 사례만 대상으로 분류합니다.
    # 완료 확인: outputs/review.json, review.md에서 사실 불일치/형식 누락/근거 누락을 확인합니다.
    # 주의: 사전 설계된 규칙 기반 점검이며 실제 생성형 AI의 진위 판정기가 아닙니다.
    # BEGIN D20-07-B01
    issues = []
    for case in CASES:
        if "sources" not in case: # 'sources' 키 자체가 딕셔너리에 없으면 'format' 오류로 처리합니다.
            kind = "format"
        elif not case["sources"]: # 키는 있으나 빈 리스트([])로 출처가 비어 있으면 'evidence' 오류로 처리합니다.
            kind = "evidence"
        elif case["answer"] != case["source"]: # 출처는 있으나 답변이 원본(source)과 다르면 'factual_mismatch' 오류로 처리합니다.
            kind = "factual_mismatch"
        else: # 모든 검증을 통과한 경우 정상('ok')으로 처리합니다.
            kind = "ok"
        issues.append({"id": case["id"], "kind": kind})
    # END D20-07-B01

    # TODO D20-07-B02: 사실성·형식·근거 검증을 서로 다른 검사라고 설명하세요.
    # 입력·대상: 제공된 F01/F02/F03 사례만 대상으로 분류합니다.
    # 완료 확인: outputs/review.json, review.md에서 사실 불일치/형식 누락/근거 누락을 확인합니다.
    # 주의: 사전 설계된 규칙 기반 점검이며 실제 생성형 AI의 진위 판정기가 아닙니다.
    # BEGIN D20-07-B02
    explanations = {
        "format": "JSON에 필수 필드가 있는지", #
        "evidence": "출처의 존재·적절성", # 
        "factual_mismatch": "확인된 원본과 주장의 불일치", # 
    }
    # END D20-07-B02
    mitigation={} # 확장용 빈 구조체(필요 시 대책 및 검증 규칙 추가 가능)를 만듭니다.
    additional_checks=[]
    agent_case={}
    trust_rules=[]

    # TODO D20-07-B03: 검증 결과와 향후 후속 수업 연결을 review.json 및 review.md로 저장하세요.
    # 입력·대상: 제공된 F01/F02/F03 사례만 대상으로 분류합니다.
    # 완료 확인: outputs/review.json, review.md에서 사실 불일치/형식 누락/근거 누락을 확인합니다.
    # 주의: 사전 설계된 규칙 기반 점검이며 실제 생성형 AI의 진위 판정기가 아닙니다.
    # BEGIN D20-07-B03
    report = {
        "classification": issues,
        "definitions": explanations,
        "mitigation": mitigation,
        "checks": additional_checks,
        "agent_case": agent_case,
        "trust_rules": trust_rules,
        "disclaimer": "교육용 규칙이며 실제 LLM 사실성 자동 판정 아님",
    }
    write_json(HERE / "outputs" / "review.json", report) # outputs/review.json 경로에 최종 리포트 저장합니다.
    lines = ["# LLM 답변 검증 결과", "", "교육용 사례의 분류 결과", ""]
    lines += [f"- {row['id']}: {row['kind']}" for row in issues] # 리스트 컴프리헨션으로 F01~F03의 분류 결과를 '- F01: factual_mismatch' 형태로 변환해 추가합니다.
    lines += ["", "## 플랫폼 연결", "FastAPI: 입력·출력 계약 / PostgreSQL: 원본 / RAG: 검색 근거 / Agent: 도구 권한(후속)"] # 아키텍처 구성 요소(FastAPI, PostgreSQL, RAG, Agent)의 역할 요약 섹션 추가합니다.
    write_md(HERE / "outputs" / "review.md", "\n".join(lines) + "\n") # 줄바꿈(\n)으로 모든 줄을 합쳐 outputs/review.md 파일로 기록
    # END D20-07-B03
    print("[07]",[(r["id"],r["kind"]) for r in issues]) # 콘솔 요약 출력합니다.

if __name__=="__main__":
    main()
