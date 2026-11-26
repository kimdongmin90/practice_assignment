"""02 · AIMessage.tool_calls / ToolMessage · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

# AI(LLM)가 외부 도구(검색기, DB 조회기 등)를 사용할 때 서로 약속된 양식(규격)에 맞춰 "주문서"를 만들고, 도구 실행 후 받은 결과에 "영수증 번호(ID)"를 짝지어 AI에게 돌려주는 연결 고리입니다.
# AI와 도구가 대화할 때 아무렇게나 말하지 않고 정해진 계약서(contracts) 양식대로 데이터를 포장하기 위해, 이미 만들어져 있는 표준 포장 함수를 불러와서 연결(래핑, Wrapping)해 주는 방식으로 작성되었습니다.
# make_request(tool_name, args, call_id) (도구 호출 주문서 만들기): AI가 어떤 도구를 어떤 재료로 실행할지 정식 요청 딕셔너리(주문서)로 만들어주는 함수입니다.
def make_request(tool_name: str, args: dict, call_id: str) -> dict: # tool_name: 실행할 도구 이름(예: "rag_search")입니다.
                                                                    # args: 도구에 넣어줄 검색어나 조건(예: {"query": "휴가 규정"})입니다.
                                                                    # call_id: 이번 요청을 구분하는 고유 번호표(예: "call_01")입니다.
    """AIMessage.tool_calls의 항목 형태. 실제로 도구를 실행하지는 않습니다."""
    from coursekit.contracts import tool_call_request # coursekit.contracts 파일 안에 미리 만들어둔 '주문서 양식 함수'를 가져옵니다.
    return tool_call_request(tool_name, args, call_id) # 표준 규격으로 예쁘게 포장된 요청 딕셔너리(dict) 형태로 출력합니다.
                                                       # 도구 이름, 재료(인자), 주문 번호를 그대로 넘겨서 완성된 주문서(dict)를 돌려줍니다.
    # TODO D29-02-B-01: AIMessage.tool_calls의 항목 형태. 실제로 도구를 실행하지는 않습니다.
    # 힌트: name, args, id가 요청값이고 tool_call_id가 결과의 연결 키입니다.


# match_result(call, result) (주문서와 실행 결과 짝짓기)
# 도구가 일을 마치고 내놓은 결과물(result)을 원래 주문서(call)와 연결해서 AI에게 보고할 결과 메시지로 만들어주는 함수입니다.
def match_result(call: dict, result: dict) -> dict:
    """실제로 DB Tool을 호출한 뒤 결과를 같은 tool_call_id에 묶습니다."""
    from coursekit.contracts import tool_result_message # coursekit.contracts 파일 안에 있는 '결과 보고서 양식 함수'를 가져옵니다.
    return tool_result_message(call, result) # 원래 요청 정보(call)와 도구 실행 결과(result)를 함께 넣어 짝지은 메시지를 돌려줍니다.
                                             # call: make_request로 만들었던 원래 요청 주문서입니다.
                                             # result: 도구가 실제로 검색하거나 조회해서 얻어낸 결과 데이터입니다.
    # TODO D29-02-B-02: 실제로 DB Tool을 호출한 뒤 결과를 같은 tool_call_id에 묶습니다.
    # 힌트: name, args, id가 요청값이고 tool_call_id가 결과의 연결 키입니다.
