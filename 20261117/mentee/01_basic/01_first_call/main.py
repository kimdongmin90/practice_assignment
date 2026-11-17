"""Day22 · 첫 실제 응답 | PPT 6~13 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""

# 전체적인 접근 방식 (큰 그림)

# 프로그램이 AI와 대화하려면 두 가지 단계가 필요합니다.
# 1. 주문서 만들기 (make_first_request): "어떤 AI를 쓸지, 무슨 규칙을 지킬지, 질문은 무엇인지"를 한 장의 메모지(딕셔너리)에 깔끔하게 적습니다.
# 2. 주문서 전달하기 (create_response): 작성한 메모지를 AI 서버에 보내고 답변을 받아옵니다.

# 준비물 챙기기 (경로 설정 및 도구 불러오기)
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded, execute_case, emit # 지금 내 파일이 어디 있는지 확인한 뒤, 두 단계 위 폴더(ROLE_ROOT)에 있는 coursekit이라는 도구 상자에서 필요한 기능(execute_case, write_json 등)을 가져옵니다.
from coursekit.io import write_json

# AI에게 보낼 주문서 만들기
def make_first_request(model, instructions, question, selected, *, structured=False): # AI에게 질문할 때 필요한 설정들을 딕셔너리(request)에 담는 함수입니다.
                                                                                      # 어떤 모델을 부를지 model 명령어로 선택합니다.
                                                                                      # AI에게 어떻게 행동해야 할지 instructions 명령어를 통해 지시합니다.
                                                                                      # 
    # TODO D22-01-B01: 첫 요청의 model·instructions·input·출력 상한·store를 완성하세요.
    # 입력·완료 기준: 입력은 전달받은 값입니다. 새 질문·임의 모델을 하드코딩하지 않으며 JSON Schema는 다음 교시입니다.
    # BEGIN D22-01-B01
    request = {"model": model, "instructions": instructions, "input": question,
               "reasoning": {"effort": "none"}, "max_output_tokens": 1200,
               "store": False, "service_tier": "default"}
    # model은 전달값, input은 question, 출력 상한1200, store=False
    return request  # 위 TODO와 raise 제거를 마친 뒤 반환합니다.
    # END D22-01-B01

def create_response(client, request, stream=False):
    # TODO D22-01-B02: Responses API를 한 번 호출하고 반환값을 돌려주세요.
    # 입력·완료 기준: 키를 직접 문자열로 쓰지 않습니다. 한 함수 호출은 create 한 번만 수행합니다.
    # BEGIN D22-01-B02
    response = client.responses.create(**request, stream=stream) # 힌트: client.responses.create(**options, stream=stream)
    return response  # 위 TODO와 raise 제거를 마친 뒤 반환합니다.
    # END D22-01-B02

def make_view(result):
    # TODO D22-01-B03: 키 없이 source·model·종료 상태·응답 ID를 요약하세요.
    # 입력·완료 기준: 미실행이면 response_id는 None입니다. 0이나 가짜 응답 ID를 채우지 않습니다.
    # BEGIN D22-01-B03
    last = result.get("attempts", [])[-1] if result.get("attempts") else {}
    summary = {"source_mode": result["source_mode"], "model": result.get("model"), "run_status": result["run_status"], "response_id": last.get("response_id")}
    # 힌트: result와 last에서 같은 필드명을 읽습니다.
    return summary  # 위 TODO와 raise 제거를 마친 뒤 반환합니다.
    # END D22-01-B03

def main():
    args=parse_args(HERE)
    result=execute_case(args,"FIRST",request_builder=make_first_request,hooks={"create":create_response})
    emit(args,result)
    view=make_view(result)
    write_json(args.output_dir/"connection_view.json",view)

if __name__=="__main__":
    guarded(main)
