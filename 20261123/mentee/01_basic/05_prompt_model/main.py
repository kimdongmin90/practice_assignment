"""실습 05 · Prompt 구성과 Chat Model 호출을 구분합니다."""

# LangChain 같은 AI 프레임워크에서는 데이터가 파이프를 타고 흐르면서 모양(자료형)이 단계별로 변신합니다. 이 코드는 그 변신 과정을 눈으로 직접 확인(관찰)하기 위해 3단계 구조로 설계되었습니다.
# 1. 재료 준비 (context_of, make_inputs): 검색해 온 규정 조각(hit)에 출처 번호를 붙여 읽기 좋은 참고 자료(context)로 만들고, 질문(question)과 함께 딕셔너리(dict) 상자에 담습니다.
# 2. 변신 및 실행 (invoke_pair):
# 	dict (재료 상자) ➔ ChatPromptValue (AI가 읽기 좋게 조립된 시험지) ➔ AIMessage (AI가 작성한 답안지) 순서로 변환합니다.
# 3. 모의고사 vs 실전 시험 선택 (--offline):
# 	--offline 옵션을 켜면 돈이 들지 않는 가짜 AI(fixture_chat_model)로 빠르게 흐름만 테스트하고, 끄면 실제 GPT 같은 AI(create_chat_model)를 호출해 관찰 기록을 남깁니다.

from pathlib import Path
import argparse
import sys

HERE = Path(__file__).resolve().parent
# 어느 폴더에서 실행해도 이 역할 폴더의 coursekit을 사용합니다.
sys.path.insert(0, str(HERE.parents[1]))

from coursekit.data import example_hit, load_hits
from coursekit.checkpoints import make_prompt
from coursekit.llm import create_chat_model
from coursekit.fixtures import fixture_chat_model, fixture_generation
from coursekit.reporting import execution_record, message_record
from coursekit.io import save_json, show_success


# 재료 상자 만들기: make_inputs & context_of
def make_inputs(question: str, context: str) -> dict:
    """입력: 질문·근거 문자열 / 출력: question, context 두 Key를 가진 dict."""
    return{"question": question, "context": context} # 사용자의 질문(question)과 방금 포장한 참고 자료(context)를 하나의 딕셔너리(dict)로 묶어 프롬프트 틀에 넣을 준비를 합니다.
    # BEGIN D26-05-B01
    # TODO D26-05-B01: 질문과 Context를 각각 question·context Key로 묶어 반환합니다.
    # 힌트: Dictionary의 두 Key 이름은 Prompt의 변수 이름과 같아야 합니다.
    # END D26-05-B01



# 핵심 실행 파이프: invoke_pair(prompt, chat_model, inputs: dict)
def invoke_pair(prompt, chat_model, inputs: dict):
    """dict → ChatPromptValue → AIMessage. 반환: (prompt_value, message)."""
    prompt_value = prompt.invoke(inputs) # 단순한 dict 재료 상자를 프롬프트 템플릿(prompt)에 넣으면, 시스템 규칙(SystemMessage)과 사용자 질문(HumanMessage)이 합쳐진 ChatPromptValue라는 완성된 시험지 객체로 변신합니다.
    message = chat_model.invoke(prompt_value) # 완성된 시험지(prompt_value)를 AI 모델(chat_model)에게 건네주면, AI가 문제를 풀고 AIMessage라는 공식 답안지 객체를 돌려줍니다.
    return prompt_value, message # 중간 결과물(prompt_value)과 최종 결과물(message)을 둘 다 반환해서, 나중에 어떻게 생겼는지 뜯어볼 수 있게 합니다.
    # BEGIN D26-05-B02
    # TODO D26-05-B02: Prompt를 먼저 실행하고 그 반환값을 Chat Model에 전달한 뒤 두 반환값을 함께 반환합니다.
    # 힌트: 첫 invoke의 반환값이 둘째 invoke의 입력입니다. 반환 순서는 (prompt_value, message)입니다.
    # END D26-05-B02


def context_of(hit: dict) -> str:
    """앞 장에서 배운 출처 포함 블록 형식입니다. 이번 실습의 제공 코드입니다."""
    return f'[{hit["citation_id"]}] {hit["source_locator"]}\n{hit["body"]}' # 검색된 자료(hit)를 AI가 보기 편하게 포장합니다.
                                                                            # 맨 앞에 [출처번호] 파일이름을 적고, 줄을 바꿔서 본문(body)을 붙여줍니다.


# 전체 실행 및 관찰 보고서 저장: main()
def main():
    parser = argparse.ArgumentParser(description="Prompt → Chat Model 입력·출력 관찰") # 터미널에서 python main.py --offline처럼 실행할 수 있게 옵션을 만듭니다.
    parser.add_argument("--offline", action="store_true", help="고정 응답 예시만 사용; 실제 모델 미실행") # --offline을 붙이면 args.offline이 True가 됩니다.
    args = parser.parse_args()
    attendance = example_hit() # 테스트할 문제(cases)를 준비합니다.
    prompt = make_prompt()
    cases = [("attendance_15", "15분 늦으면 어떻게 기록되나요?", attendance)] # "15분 늦으면 어떻게 기록되나요?"라는 질문과 출석 규정 자료 attendance를 짝지음
    # 모델 생성·호출 전에 로컬 TODO와 입력을 먼저 확인합니다.
    prepared = [(case_id, make_inputs(question, context_of(hit)), hit)
                for case_id, question, hit in cases] # 리스트 컴프리헨션을 통해 inputs 딕셔너리 형태로 미리 변환해 prepared에 담아둡니다.
    observations = {}
    # 기본 경로는 실제 모델입니다. 환경 문제가 있어도 자동으로 예시로 전환하지 않습니다.
    chat_model = fixture_chat_model() if args.offline else create_chat_model() # fixture_chat_model(오프라인 모드면 연습용 가짜 모델), 아니면 create_chat_model(실제 LLM)을 선택합니다.
    records = []
    for case_id, inputs, hit in prepared:
        prompt_value, message = invoke_pair(prompt, chat_model, inputs)
        records.append({
            "case_id": case_id,
            "question": inputs["question"],
            "context": inputs["context"],
            "prompt_value_type": type(prompt_value).__name__,
            "prompt_messages": [{"type": m.type, "content": m.content}
                                for m in prompt_value.to_messages()],
            "response": message_record(message),
            "evidence": {"citation_id": hit["citation_id"],
                         "doc_id": hit["doc_id"], "source_locator": hit["source_locator"],
                         "body": hit["body"]},
            "human_evidence_review": "pending",
        }) # type(prompt_value).__name__ 명령어로 프롬프트 결과물의 실제 자료형 이름("ChatPromptValue")이 맞는지 기록합니다.
           # prompt_value.to_messages() 명령어로 시험지 안에 들어있는 메시지들(system, human)을 하나씩 꺼내 실제 AI에게 어떤 문장이 전달되었는지 기록합니다.
           # human_evidence_review: "pending" 명려어로 AI가 답변을 내놓았더라도 내용이 진짜 맞는지 사람이 직접 원문과 대조해 검토해야 한다(pending, 대기 중)는 표시를 남깁니다.
    result = {
        "exercise": "05_prompt_model",
        "execution": execution_record("offline_fixture" if args.offline else "live", llm=not args.offline),
        "real_model_calls": 0 if args.offline else len(records),
        "fixed_example_calls": len(records) if args.offline else 0,
        "observations": observations,
        "cases": records,
        "review_note": "문장·출처의 정답 여부는 자동 판정하지 않았습니다. reports/review.md에 원문 대조를 기록하세요.",
    } # real_model_calls(실제 돈이 드는 API 호출 횟수)와 fixed_example_calls(연습용 호출 횟수)를 정확히 구분해서 기록한 뒤, prompt_model.json 파일로 저장합니다.
    path = save_json(HERE, "prompt_model.json", result)
    show_success("05 Prompt·Chat Model 관찰 기록", path)
    print("실제 LLM 실행:", not args.offline, "| 원문 대조: 수강생 확인 필요")


if __name__ == "__main__":
    main()
