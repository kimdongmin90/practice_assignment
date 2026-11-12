"""파일 역할 이해·분리. 실행: python -m uvicorn main:app --reload"""
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


app = FastAPI(title="Knowledge API", description="AI 플랫폼의 원본 지식 관리 연습")

@app.get("/health")
def health():
    # 이 경로의 응답 확인입니다. 파일·DB·AI 모델의 전체 상태 점검은 아닙니다.
    return {"status": "ok"}

@app.get("/api/knowledge")
def list_knowledge():
    with LOCK:
        data = read_data()
    # 파일 전체에는 내부용 next_id도 있으므로 entries만 응답합니다.
    return data["entries"]

@app.get("/api/knowledge/{knowledge_id}")
def get_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
    for entry in data["entries"]:
        same_id = entry["id"] == knowledge_id
        if same_id:
            return entry
    # 입력은 정수이지만 저장된 항목이 없으면 404입니다. foo 같은 Path는 먼저 422입니다.
    raise HTTPException(404, "Knowledge not found")

@app.post("/api/knowledge", status_code=201, response_model=Knowledge)
def create_knowledge(payload: KnowledgeWrite):
    # 하나의 잠금으로 현재 데이터 읽기 → ID 발급 → 저장을 함께 보호합니다.
    with LOCK:
        data = read_data()
        entry = payload.model_dump()
        entry["id"] = data["next_id"]
        data["entries"].append(entry)
        data["next_id"] += 1
        write_data(data)
    # 201을 선언하는 것만으로 저장되지는 않습니다. 실제 저장 성공 뒤 응답합니다.
    return entry

@app.put("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def update_knowledge(knowledge_id: int, payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            same_id = entry["id"] == knowledge_id
            if same_id:
                updated = payload.model_dump()
                updated["id"] = knowledge_id
                data["entries"][i] = updated
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
                return Response(status_code=204)
    raise HTTPException(404, "Knowledge not found")
