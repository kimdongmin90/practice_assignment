"""Day22 · Streaming과 완료 판정 | PPT 24~31 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded, execute_case, emit
from coursekit.response import get

def receive_event(state, event, clock, started):
    state.events_seen += 1
    kind = get(event,"type")
    if kind == "response.output_text.delta":
        # TODO D22-03-B01: 비어 있지 않은 첫 텍스트의 시간과 delta를 누적하세요.
        # 입력·완료 기준: clock은 단조 시계입니다. 빈 delta를 첫 표시로 세지 않습니다.
        # BEGIN D22-03-B01
        delta = get(event, "delta", "")
        if not isinstance(delta, str):
            state.error = "stream_protocol_error"
            return
        if delta and state.first_text_ms is None:
            state.first_text_ms = (clock() - started) * 1000
        state.parts.append(delta) # state.parts.append(...)로 누적. delta 개수는 Token 수가 아닙니다.
        # END D22-03-B01
    elif kind in {"response.completed","response.incomplete","response.failed"}:
        # TODO D22-03-B02: 최종 이벤트의 Response를 보관하세요.
        # 입력·완료 기준: 부분 문자열을 합쳤다고 completed를 직접 만들어서는 안 됩니다.
        # BEGIN D22-03-B02
        # 중복 terminal이면 오류, 아니면 state.final에 event.response 저장
        if state.final is not None:
            state.error = "duplicate_terminal_event"
        state.final = get(event, "response")
        # END D22-03-B02
    elif kind == "error":
        state.error="stream_error"

def streaming_choice():
    # TODO D22-03-B03: 실제 스트리밍을 요청하도록 선택값을 반환하세요.
    # 입력·완료 기준: 메시지 UI를 새로 만드는 실습이 아닙니다. 최종 상태·부분 파일·first_text_ms를 확인합니다.
    # BEGIN D22-03-B03
    return True # 
    # END D22-03-B03

def main():
    args=parse_args(HERE)
    modes=[streaming_choice()]
    observations=[]
    for use_stream in modes:
        result=execute_case(args,args.case or "H01",stream=use_stream,hooks={"event":receive_event})
        emit(args,result)

if __name__=="__main__":
    guarded(main)
