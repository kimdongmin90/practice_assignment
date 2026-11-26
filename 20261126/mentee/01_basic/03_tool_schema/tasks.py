"""03 · @tool·Pydantic·JSON Schema · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

# AI(LangChain Agent)가 데이터베이스(DB)에 있는 보고서 상태를 직접 조회할 수 있도록 '전용 도구(Tool)'를 만들어서 포장해 주는 코드입니다.
# AI에게 회사 데이터베이스(DB)를 마음대로 뒤지게 하면 위험할 수 있습니다. 그래서 안전장치가 달린 전용 리모컨(Tool) 하나만 쥐여주는 방식으로 설계했습니다.
# 1. 안전장치 만들기 (validate_id): AI가 이상한 번호(예: 음수나 글자)를 입력하지 못하게 번호표를 먼저 검사합니다.
# 2. AI용 도구 포장하기 (register_status_tool): 일반 파이썬 함수에 @tool이라는 특별한 이름표를 붙여서, AI가 *"아, 이건 보고서 상태를 조회할 때 쓰는 도구구나!"*라고 알아보고 버튼을 누를 수 있게 만듭니다.
# 3. 글자(JSON)로 변환하기: DB에서 꺼낸 파이썬 데이터는 AI가 읽기 어려울 수 있으므로, 표준 글자 양식(JSON)으로 예쁘게 바꿔서 돌려줍니다.

# validate_id(report_id) (번호표 검사기)
# AI가 넘겨준 보고서 번호(report_id)가 진짜 올바른 번호인지 검사하고 정리해 주는 함수입니다.
def validate_id(report_id: int) -> int:
    """실제 reports.report_id인 양의 정수만 허용합니다."""
    from coursekit.contracts import report_id_from # coursekit.contracts 파일에서 번호 검사 규칙 함수를 가져옵니다.
    return report_id_from(report_id)
    # TODO D29-03-B-01: 실제 reports.report_id인 양의 정수만 허용합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.

# register_status_tool() (AI 전용 도구 조립 공장)
# 안쪽에 실제 일을 하는 함수(lookup_status)를 만들고, @tool 스티커를 붙여서 AI에게 건네주는 함수입니다.
def register_status_tool():
    """@tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다."""
    from langchain.tools import tool # AI용 도구로 변신시켜 주는 스티커(@tool)입니다.
    import json # 데이터를 글자(JSON)로 바꿔주는 번역기입니다.
    from coursekit.db import fetch_report_status # 실제 DB에서 상태를 꺼내오는 함수입니다.
    # @tool 스티커를 붙여서 AI가 인식할 수 있는 도구로 만듭니다.
    @tool
    def lookup_status(report_id:int) -> str:
        """기존 보고서 report_id의 인덱싱 상태를 읽기 전용 조회합니다. task_id가 아닙니다."""
        return json.dumps(fetch_report_status(validate_id(report_id)), ensure_ascii=False, default=str) # 실행 순서(안쪽 괄호부터 바깥쪽으로 실행됩니다!):
                                                                                                        # 1단계: validate_id(report_id) -> 번호가 정상인지 검사합니다.
                                                                                                        # 2단계: fetch_report_status(...) -> 검사 통과한 번호로 DB에서 상태 조회합니다.
                                                                                                        # 3단계: json.dumps(...) -> DB 결과를 한글이 깨지지 않는 JSON 글자로 변환해 반환합니다.
    return lookup_status # 완성된 'lookup_status' 도구를 바깥으로 내보냅니다.
    # TODO D29-03-B-02: @tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.
