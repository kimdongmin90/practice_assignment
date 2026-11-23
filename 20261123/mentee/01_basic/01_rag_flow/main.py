"""Day26 실습. 실행 위치와 관계없이 현재 역할 폴더의 지원 모듈을 사용합니다."""

# AI가 거짓말(환각)을 하지 않고 정확한 교과서 내용만 보고 대답하게 만들려면 5단계 작업 흐름이 필요합니다. 이 코드는 두 가지 핵심 기능을 구현해 전체 흐름을 검증합니다.
# 1. 작업 순서 바로잡기 (stage_order): 뒤죽박죽 섞여 있는 5가지 AI 작업 카드(STAGE_CARDS)를 올바른 실행 순서대로 줄 세웁니다.
# 2. 근거 메모지 작성하기 (evidence_note): 검색으로 찾아온 실제 규정(hit)에서 "이 문장이 어느 문서의 몇 번 출처인지, 어떤 예외 사항을 조심해야 하는지"를 한눈에 볼 수 있는 근거 확인 카드로 정리합니다.

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))
from coursekit.io import save_json, show_success
from coursekit.data import example_hit, load_hits
from coursekit.reporting import execution_record

# 입력·출력 설명은 제공됩니다. TODO에서는 올바른 처리 순서를 연결합니다.
# 뒤죽박죽 섞인 작업 카드 상자 (STAGE_CARDS)
STAGE_CARDS = {
    "Generator": {"input": "모델 입력", "output": "생성된 답변"},
    "Prompt": {"input": "규칙·질문·Context", "output": "모델이 읽을 메시지"},
    "Retriever": {"input": "질문·검색 조건", "output": "관련 청크 후보"},
    "Validator · Source 연결": {"input": "생성 결과·허용 ID", "output": "검증 결과·원문 위치"},
    "Context Builder": {"input": "후보 목록", "output": "선택한 근거·포함 ID"},
} # AI가 일하는 5가지 부서의 역할(input 재료와 output 결과물)을 적어둔 사전(딕셔너리)입니다.(지금은 순서가 뒤섞여 있습니다.)

# 올바른 작업 순서대로 줄 세우기: stage_order()
def stage_order() -> list[str]: # AI가 똑똑하게 대답하는 황금 순서 5단계를 리스트로 반환합니다.
    """STAGE_CARDS의 이름 다섯 개를 처리 순서대로 반환합니다."""
    return ["Retriever", "Context Builder", "Prompt", "Generator", "Validator · Source 연결"] # Retriever(자료 검색기): 질문과 관련된 참고 자료 후보들을 찾아옵니다.
                                                                                             # Context Builder(참고자료 편집기): 찾아온 후보 중 진짜 쓸만한 핵심 근거만 골라 번호표(ID)를 붙입니다.
                                                                                             # Prompt(질문지 조립기): "이 규칙을 지키고, 방금 고른 참고자료만 보고 이 질문에 답해"라며 AI에게 줄 시험지를 만듭니다.
                                                                                             # Generator(AI 답변 생성기): 시험지를 읽은 LLM(ChatGPT 같은 모델)이 실제로 답변을 작성합니다.
                                                                                             # Validator · Source 연결(검사기 및 출처 확인): AI가 지어낸 말은 없는지, 답변에 적힌 출처 번호가 아까 골라준 참고자료 목록(허용 ID)에 진짜 있는지 마지막으로 채점합니다.
    # BEGIN D26-01-B01
    # TODO D26-01-B01: 다섯 단계의 이름을 처리 순서대로 반환합니다.
    # 힌트: 검색 → 근거 선택 → 메시지 작성 → 생성 → 확인 순서입니다.
    # 함수의 docstring·README·expected/EXPECTED.md에서 입력과 완료 조건을 확인하세요.
    # END D26-01-B01

# 근거 확인 메모지 만들기: evidence_note(hit: dict)
def evidence_note(hit: dict) -> dict: # Retriever가 찾아온 실제 규정 조각(hit) 하나를 받아서, 사람이 검증하기 편한 근거 확인표로 바꿉니다.
    """출석 문서와 사람이 읽은 판단을 함께 기록합니다. 모델 호출 결과가 아닙니다.""" # • hit 안에 들어있는 원본 출처 번호(citation_id), 문서 이름(doc_id), 버전(source_version), 위치(source_locator), 본문 내용(body)은 그대로 옮겨 적고, 판단 결과("지각")와 함께 반드시 사람이 추가로 확인해야 할 예외 조건("사전 승인을 받은 경우 운영실 확인")을 함께 기록합니다.
    return {"citation_id": hit["citation_id"], "doc_id": hit["doc_id"], "source_version": hit["source_version"], "source_locator": hit["source_locator"], "evidence": hit["body"], "question":"지각", "judgment": "지각", "exception_to_check":"사전 승인을 받은 경우 운영실 확인"} # 
    # BEGIN D26-01-B02
    # TODO D26-01-B02: 입력 Hit의 출처·본문과 15분 질문의 판단·예외를 한 dict로 묶습니다.
    # 힌트: source_locator와 body를 그대로 읽고, 문서의 “까지”와 사전 승인 조건을 확인하세요.
    # 함수의 docstring·README·expected/EXPECTED.md에서 입력과 완료 조건을 확인하세요.
    # END D26-01-B02

# 전체 조립 및 보고서 저장: main()
def main():
    order = stage_order()
    report = {
        "execution": execution_record("concept_review"),
        "stages": [{"stage": name, **STAGE_CARDS[name]} for name in order], # 아까 정한 올바른 순서(order)대로 이름을 하나씩 꺼낸 뒤, STAGE_CARDS[name] 안에 들어있던 input과 output 정보를 꺼내서(**) 한 줄짜리 깔끔한 카드로 합칩니다.
        "case": evidence_note(example_hit()), # 연습용 샘플 검색 결과(example_hit())를 넣어 근거 메모지를 만듭니다.
        "observation": "사람이 강의 원문을 읽고 작성한 역할·근거 확인표",
    }
    path = save_json(HERE, "rag_flow.json", report) # 완성된 전체 흐름표와 사례를 rag_flow.json 파일로 저장합니다.
    show_success("01 Basic", path) # 성공 메시지를 출력합니다.

if __name__ == "__main__":
    main()
