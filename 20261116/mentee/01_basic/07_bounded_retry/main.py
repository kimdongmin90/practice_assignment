"""Day21 실습 07: 실패 분류·최대 2회. 실행: python main.py"""

# 핵심 접근 방식 (Design Approach)

# 제한된 자동 복구 (Bounded Retry): 무한 재시도로 인한 API 비용 낭비와 지연 시간을 막기 위해 최대 실행 횟수를 2회(최초 1회 + 수정 재시도 1회)로 엄격히 제한합니다.
# 오류 유형별 타겟 수정 (Targeted Prompt Repair): 모든 실패를 무작정 재시도하지 않고, 프롬프트 지시만으로 고칠 수 있는 형식/구조 오류(json_error, schema_error)만 선별하여 맞춤형 교정 문구를 추가합니다.
# 환각 방지 가드레일 (Anti-Hallucination Guardrail): 출력을 고치는 과정에서 모델이 없는 사실을 지어내거나 원래 질문의 의도를 벗어나지 않도록 명시적인 제약 조건을 함께 부여합니다.
# 실행 이력 추적 (Audit & Observability): 매 시도마다 결과물, 에러 코드, 그리고 프롬프트의 변경 여부를 확인할 수 있는 SHA-256 해시값을 기록하여 디버깅과 검증을 용이하게 만듭니다.
# 픽스처 기반 테스트 (Fixture-based Testing): 실제 모델 대신 validation_fixtures.json에 정의된 4가지 시나리오별 고정 응답을 주입하여, 매번 동일한 테스트 결과를 보장합니다.
# 단언문(assert)을 통한 계약 검증: 각 시나리오가 실행된 횟수(calls)가 [2, 2, 1, 1]인지 코드로 강제 검증하여, 재시도해야 할 때 재시도하고 멈춰야 할 때 즉시 멈추는지 확인합니다.
# 결과 아티팩트 저장: 검증이 통과된 실행 결과를 outputs/retry_results.json에 저장하여 추후 채점이나 로그 감사(Audit)에 활용할 수 있도록 남깁니다.

from pathlib import Path
import sys

# 경로 설정 및 유틸리티 임포트
HERE = Path(__file__).resolve().parent # 현재 실행 중인 파일의 위치를 기준으로 ROLE_ROOT(두 단계 상위 폴더)를 sys.path(파이썬 모듈 검색 경로)에 추가합니다.
                                       # 어느 위치에서 스크립트를 실행하더라도 coursekit 패키지의 sha_text 같은 함수를 안정적으로 불러오기 위한 설정입니다.
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))
from coursekit.io import DATA, read_json, write_json, sha_text, run

# 기준: Day21 PPT 56~63장. 실제 모델 호출/실습 데이터 수정은 하지 않습니다.
# outputs는 실행 시 생성됩니다. 05/08의 모델 응답은 직접 수집한 원문만 등록합니다.
from coursekit.retry import run_fixture_scenarios

# 프롬프트 교정 함수
def repair_prompt(original, error): # safe 딕셔너리에 정의된 두 가지 형식 오류 외에 다른 오류(예: 내용 부실, 안전 정책 위반 등)가 들어오면 ValueError를 발생시켜 잘못된 프롬프트 변형을 차단합니다.
                                    # original(기존 프롬프트) 뒤에 [수정 요청] 블록을 추가합니다.
                                    # 이때 기존 맥락 유지, 오류별 구체적 해결책(safe[error]), 그리고 할루시네이션(사실 창작) 금지 지침을 결합해 반환합니다.
    # TODO D21-07-B01: 허용한 형식 오류만 안전한 한 문장 요약으로 수정 요청을 만드세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: unknown_source는 자동 형식 수정 요청을 만들지 않습니다.
    # BEGIN D21-07-B01
    safe = {
        "json_error":"JSON 객체 하나를 코드 블록 없이 출력하세요.",
        "schema_error":"필수 필드·자료형·길이를 지키세요. source_ids는 양의 정수 목록입니다.",
    }
    if error not in safe:
        raise ValueError("형식 오류만 수정 요청을 만듭니다")
    repaired = original + "\n[수정 요청] 같은 질문·지식·계약을 유지하세요. "+safe[error]+" 부족한 사실은 만들지 마세요."
    # 이전 원문 전체, traceback, 비밀 값은 붙이지 않습니다.
    # END D21-07-B01
    return repaired

# 실행 및 재시도 제어 함수
def run_with_retry(generate, prompt, validate):
    # TODO D21-07-B02: 최초 1회+수정 1회까지만 반복하고 통과하지 못하면 None을 반환하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 호출 수가 최대 2. 정상 정보 부족도 1회에 종료.
    # 핵심: 성공 반환은 자동 구조·참조 통과일 뿐입니다. 근거를 맞게 읽었는지 사람 검토가 남습니다.
    # BEGIN D21-07-B02
    history = []
    for attempt in (1,2): # generate(prompt)로 모델 응답(raw)을 생성하고 validate(raw)로 파싱 및 스키마 검증을 수행합니다.('attempt = 1' 일 때)
        raw = generate(prompt)
        obj, error = validate(raw)
        history.append({"attempt":attempt,"error":error,"raw_text":raw,"prompt_sha256":sha_text(prompt)}) # 시도 횟수, 에러 종류, 원본 응답, 그리고 sha_text(prompt)를 통해 1회차와 2회차에 서로 다른 프롬프트가 사용되었음을 증명하는 해시 지문을 남깁니다.
        if error is None: # 검증을 통과하면 파싱된 obj(객체)와 history(기록)을 즉시 반환합니다.(조기 종료 및 분기처리)
            return obj, history
        if error not in {"json_error", "schema_error"} or attempt == 2: # 고칠 수 없는 오류이거나 이미 2번째 시도까지 마쳤다면 루프를 탈출(break)합니다.
            break # 
        prompt = repair_prompt(prompt, error) # 복구 가능한 오류이고 1회차 시도였다면, repair_prompt로 프롬프트를 수정하여 prompt 변수에 덮어쓴 뒤 2회차 루프를 실행합니다.(프롬프트 갱신 후 2회차 진입)
                                              # 2회차마저 실패하면 최종적으로 None과 전체 실패 이력(history)을 반환합니다.
    return None, history 
    # END D21-07-B02

def main():
    # 테스트 시나리오 데이터 로드
    fixtures=read_json(DATA/"validation_fixtures.json") # DATA 폴더에 있는 validation_fixtures.json 파일을 읽어옵니다.
                                                        # 여기에는 주석에 명시된 4가지 테스트 케이스가 순서대로 들어 있습니다.
    # TODO D21-07-B03: 네 fixture 순서의 호출 수 2·2·1·1을 확인하고 기록하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 복구 성공·연속 실패·규칙 중단·부족 정상 종료 네 경우.
    # BEGIN D21-07-B03
    # 시니리오 실행
    results = run_fixture_scenarios(fixtures, runner=run_with_retry) # coursekit.retry에서 가져온 run_fixture_scenarios() 함수에 fixtures(테스트 데이터)와 우리가 구현한 재시도 제어 함수(run_with_retry)를 전달하여 실행합니다.
                                                                     # 각 시나리오마다 run_with_retry가 몇 번 호출되었는지(calls), 최종 성공 여부, 시도 이력(history) 등이 담긴 리스트(results)가 반환됩니다.
    # 4가지 시나리오별 호출 횟수 검증 ([2, 2, 1, 1])
    assert [x["calls"] for x in results] == [2, 2, 1, 1] # 1. 복구 성공(calls == 2): 1회차에 json_error 또는 schema_error가 발생해 repair_prompt로 프롬프트를 수정하고, 2회차 재시도에서 검증을 통과(error is None)하여 총 2회 호출 후 정상 종료됩니다.
                                                         # 2. 연속 실패연속 실패(calls == 2): 1회차에 형식 오류가 발생해 프롬프트를 수정하고 재시도 후, 2회차에서도 또다시 오류가 발생했지만, 최대 시도 횟수(attempt == 2)에 도달했으므로 루프를 종료(break)하여 총 2회 호출 후 실패로 끝납니다.
                                                         # 3. 규칙 중단(calls == 1): 1회차에서 형식 오류가 아닌 다른 오류(예: 금지어 포함, 정책 위반 등 safe에 없는 오류)가 발생했고, error not in {"json_error", "schema_error"} 조건에 걸려 재시도하지 않고 즉시 루프를 탈출하므로 1회 호출 후 종료됩니다.
                                                         # 4. 부족 정상 종료(calls == 1): 1회차 응답에서 내용이 부족하더라도 스키마 규칙 자체는 정상(error is None, 예: 빈 리스트 [] 또는 정보 없음 상태 반환)으로 통과하고 오류가 없으므로 재시도 없이 1회 호출만으로 즉시 결과를 반환하고 종료됩니다.
    # 결과 저장 및 안전한 실행 래퍼
    write_json(HERE/"outputs"/"retry_results.json", {"source_mode":"fixture","results": results}) # assert(검증)을 무사히 통과하면, 현재 파일 위치(HERE) 아래 outputs/retry_results.json 경로에 실행 모드("fixture")와 상세 결과를 JSON 파일로 저장합니다.
    # END D21-07-B03
    print("[07] 제어 흐름만 검증했습니다. 실제 모델 복구율은 측정하지 않았습니다.")

if __name__ == "__main__":
    run(main) # coursekit.io의 run 유틸리티를 통해 예외 처리나 실행 환경을 감싸서 main() 함수를 안전하게 실행하는 진입점입니다.
