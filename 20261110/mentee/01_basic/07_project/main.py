"""함께 통합하고 프로젝트 준비. 실행: python -m uvicorn main:app --reload"""
# 1. 라이브러리 및 외부 모듈 임포트 (Import) 구역
from fastapi import FastAPI, HTTPException, Response # 파이썬 기반 고성능 웹 API 프레임워크 fastapi에서 FastAPI(서버 본체), HTTPException(에러 제어), Response(상태 코드 응답) 객체를 가져옵니다.
from storage import LOCK, read_data, write_data # storage.py(이 프로젝트 전용 파일 읽기/쓰기 모듈 (사전에 멘토/과제 측에서 제공한 툴))에서 LOCK(동시 접근 제어), read_data(JSON 읽기 함수), write_data(JSON 쓰기 함수)를 가져옵니다.

from pydantic import BaseModel, Field # 데이터 검증(Validation) 및 설정을 위한 파이썬 라이브러리 pydantic에서BaseModel(데이터 모델 설계 기본 클래스), Field(세부 제약조건 설정 함수)를 가져옵니다.

# 2. Pydantic 데이터 모델(DTO) 정의 구역
# 입력 모델은 HTTP Body의 규칙입니다. DB 테이블이나 저장 코드가 아닙니다.
class KnowledgeWrite(BaseModel): # 클라이언트가 데이터를 '보낼 때(Write)' 검증하기 위한 데이터 형태 정의합니다.
    title: str = Field(min_length=1, max_length=80) # title에 문자열 변수 / 최소 1자 이상, 최대 80자 이하만 허용하는 Field 설정하여 공백이나 빈 값을 보낼 수 없도록 차단하고 데이터베이스 버퍼 오버플로우를 예방합니다.
    content: str = Field(min_length=1, max_length=2000) # content에 문자열 변수 / 본문 내용으로 최소 1자, 최대 2000자 이하만 허용하여 글자 수 제한이 명확한 게시글, 지식 데이터를 안전하게 포매팅합니다.
    category: str = Field(min_length=1, max_length=30) # category에 문자열 변수 / 지식의 분류 태그로 최소 1자, 최대 30자 이하만 허용하여 데이터 그룹화(예: 'Python', 'FastAPI')를 위한 유효한 텍스트만 받습니다.


class Knowledge(KnowledgeWrite): # 클라이언트에게 데이터를 '돌려줄 때(Response)' 사용할 모델 (ID 포함), KnowledgeWrite 클래스를 상속받음으로써 title, content, category 필드를 그대로 이어받습니다.
    id: int # 정수형 변수 / 시스템이 내부적으로 부여한 고유 번호 id는 클라이언트가 데이터를 전송할 때는 지정할 수 없고, 조회할 때만 결과에 포함되어 내려갑니다.


# 3. FastAPI 인스턴스 생성 및 초기화
app = FastAPI(title="Knowledge API", description="AI 플랫폼의 원본 지식 관리 연습") # FastAPI() 함수로 웹 서버를 기동하고 엔드포인트를 관리하는 핵심 인스턴스 객체를 생성하고 title과 description 인자를 채워넣으면 자동으로 빌드되는 /docs(Swagger UI) 문서 상단에 표기됩니다.

# 4. 라우터 및 API 엔드포인트 구현 구역 (조회)
@app.get("/health") # HTTP GET 요청(데이터 조회)을 처리하는 라우터 데코레이터 @app.get을 사용해 브라우저 주소창이나 API 클라이언트로 '서버주소/health'에 접근할 때 작동합니다.
def health():
    # 이 경로의 응답 확인입니다. 파일·DB·AI 모델의 전체 상태 점검은 아닙니다.
    return {"status": "ok"} # 서버가 죽지 않고 잘 살아있는지 확인(Health Check)하는 가벼운 엔드포인트입니다.
                            # JSON 형식으로 정상 작동 상태(`ok`)를 반환합니다.

@app.get("/api/knowledge") # @app.get로 '서버주소/api/knowledge' 경로로 들어오는 GET 요청 매핑합니다.
def list_knowledge():
    with LOCK: # 데이터 파일에 여러 요청이 동시에 접근하여 파일이 깨지는 경쟁 상태(Race Condition)를 차단하기 위한 락을 획득합니다.
        data = read_data() # read_data() 함수로 스토리지 파일(JSON)의 전체 딕셔너리 데이터를 메모리로 읽어옵니다.
    # 파일 전체에는 내부용 next_id도 있으므로 entries만 응답합니다.
    # BEGIN B07-01
    # TODO B07-01: 통합 목록 Route에서 entries만 응답하도록 연결하세요.
    # 아래 미완성 표시를 지우고 요구한 코드를 작성하세요.
    return data["entries"]
    # END B07-01

@app.get("/api/knowledge/{knowledge_id}") # HTTP GET 요청(특정 자원의 조회)을 처리하는 라우터 데코레이터(경로 지정자) @app.get로 "/api/knowledge/{knowledge_id}": 중괄호`{}`는 경로 매개변수(Path Parameter)로, 사용자가 입력한 값을 변수로 받습니다.
                                          # 브라우저나 클라이언트가 주소창에 'http://127.0.0 요청을 보내면 작동합니다.
def get_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
    for entry in data["entries"]:
        same_id = entry["id"] == knowledge_id
        if same_id:
            return entry
    # 입력은 정수이지만 저장된 항목이 없으면 404입니다. foo 같은 Path는 먼저 422입니다.
    raise HTTPException(404, "Knowledge not found")

# 5. 과제 해결을 위해 추가해야 하는 핵심 CRUD 엔드포인트 풀이
@app.post("/api/knowledge", status_code=201, response_model=Knowledge) # HTTP POST 요청(데이터 생성)을 처리하는 데코레이터 @app.post로 status_code=201: 리소스 생성 성공 표준 규격인 '201 Created' 코드를 응답 헤더에 세팅합니다.
                                                                       # response_model=Knowledge로 반환하는 리턴값이 최종적으로 ID를 포함한 규칙에 맞는지 한 번 더 엄격히 검사합니다.
def create_knowledge(payload: KnowledgeWrite):
    # 하나의 잠금으로 현재 데이터 읽기 → ID 발급 → 저장을 함께 보호합니다.
    with LOCK: # 가상 DB 데이터를 안전하게 수정하기 위해 상호 배제(Lock) 처리 진입합니다.
        data = read_data() # 현재 스토리지 파일의 상태(기존 데이터 목록, 다음 부여될 ID 값 등)를 읽어옵니다.
        entry = payload.model_dump() # model_dump() 메서드로 Pydantic 객체를 파이썬의 표준 딕셔너리(`{key: value}`) 구조로 변환합니다.
        entry["id"] = data["next_id"] # 저장소 딕셔너리 내에 미리 준비된 다음 고유 번호(`data["next_id"]`)를 가져와 새 데이터의 'id' 필드로 강제 주입합니다.
        data["entries"].append(entry) # 파이썬 리스트의 append() 함수를 이용하여 전체 목록 배열 맨 마지막 자리에 새 데이터를 추가합니다.
        data["next_id"] += 1 # 다음 번에 새 데이터가 들어올 때 중복되지 않도록 고유 ID 카운터를 1 증가시킵니다.
        # BEGIN B07-02
        # TODO B07-02: 생성된 지식과 증가한 next_id를 파일에 함께 저장하세요.
        # 아래 미완성 표시를 지우고 요구한 코드를 작성하세요.
        write_data(data) # write_data()로 수정한 파이썬 딕셔너리를 영구적인 물리 파일(JSON)로 덮어써서 기록합니다.
        # END B07-02
    # 201을 선언하는 것만으로 저장되지는 않습니다. 실제 저장 성공 뒤 응답합니다.
    return entry # 완벽히 저장 처리가 끝난 뒤, 생성된 딕셔너리 객체(`entry`)를 클라이언트에 전달해 줍니다.

@app.put("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def update_knowledge(knowledge_id: int, payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            same_id = entry["id"] == knowledge_id
            if same_id:
                updated = payload.model_dump()
                updated["id"] = knowledge_id
                # BEGIN B07-03
                # TODO B07-03: 같은 ID의 위치 i를 updated로 교체하세요.
                # 아래 미완성 표시를 지우고 요구한 코드를 작성하세요.
                data["entries"][i] = updated
                # END B07-03
                write_data(data)
                return updated
    # 없는 ID를 새로 생성하지 않습니다. PUT에서도 세 입력 필드가 모두 필수입니다.
    raise HTTPException(404, "Knowledge not found")

@app.delete("/api/knowledge/{knowledge_id}", status_code=204)
def delete_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                data["entries"].pop(i)
                write_data(data)
                # BEGIN B07-04
                # TODO B07-04: 삭제 저장 후 본문 없는 204 응답을 반환하세요. dict 또는 JSON 문자열을 넣지 마세요.
                # 아래 미완성 표시를 지우고 요구한 코드를 작성하세요.
                return Response(status_code=204)
                # END B07-04
    raise HTTPException(404, "Knowledge not found")
