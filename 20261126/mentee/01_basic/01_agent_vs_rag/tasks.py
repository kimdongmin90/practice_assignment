"""01 · AI Agent vs 고정 RAG/Workflow · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

# 질문 의도 분류(classify_request)와 실행 전략 계획(plan_for_request)을 규칙 기반(Rule-based) 라우터로 구현한 코드
# classify_request(question) (질문 분류기): 사용자의 질문(question)을 받아서 'agent', 'db', 'rag' 중 딱 하나의 이름표를 붙여주는 함수
def classify_request(question: str) -> str:
    """질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent. """
    q = question.lower() # 영어 대소문자 구분을 없애기 위해 모두 소문자로 바꿉니다.(예: "Ready" -> "ready")
    has_db = any(t in q for t in ('상태', '인덱싱', 'revision', 'ready', 'pending')) # 상태 확인'과 관련된 단어가 하나라도 들어있는지 검사합니다. (결과: True 또는 False)
    has_doc = any(t in q for t in ('찾아', '내용', '설명', '근거', '검색')) # '문서 검색'과 관련된 단어가 하나라도 들어있는지 검사합니다. (결과: True 또는 False)
    if has_db and has_doc: return 'agent' # 두 조건이 모두 참이면 'agent', 상태만 참이면 'db', 나머지는 모두 'rag'를 돌려줍니다.
    if has_db: return 'db'
    return 'rag'
    # TODO D29-01-B-01: 질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.


# plan_for_request(question) (실행 계획표 작성기): 앞선 함수가 붙여준 이름표(mode)를 보고, 실제로 사용할 도구 목록(tools)과 전략을 딕셔너리(사전) 형태의 계획표로 포장해 주는 함수
def plan_for_request(question: str) -> dict:
    """처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다."""
    mode= classify_request(question) # 첫 번째 함수를 불러서 질문의 종류('rag', 'db', 'agent' 중 하나)를 알아냅니다.
    tools= {'rag':['rag_search'], 'db':['lookup_status'], 'agent':['rag_search', 'lookup_status']}[mode] # 종류별로 필요한 도구(함수 이름)를 짝지어 놓은 메뉴판에서 해당 도구를 꺼냅니다.
                                                                                                         # 문서 검색 도구만 사용
                                                                                                         # 상태 조회 도구만 사용
                                                                                                         # 두 도구 모두 사용
    return {'strategy': mode, 'tools': tools, 'decision':'고정 조건에 따른 실습용 계획; 실제 Agent 선택은 06에서 LLM 수행'} # 최종 계획표를 딕셔너리 형태로 만들어 돌려줍니다.
    # TODO D29-01-B-02: 처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.