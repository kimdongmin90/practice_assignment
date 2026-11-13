from fastapi import FastAPI, HTTPException, Response
from storage import LOCK, read_data, write_data

from pydantic import BaseModel, Field


class KnowledgeWrite(BaseModel):
    # 세 필드는 모두 필수입니다. 길이 규칙은 공백 제거 규칙과 다릅니다.
    id: int
    title: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=30)


class Knowledge(KnowledgeWrite):
    id: int

app = FastAPI(title="Day19 AM Knowledge API - Basic")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/knowledge", response_model=list[Knowledge]) # 반환되는 리스트의 각 요소가 knowledge 모델 스키마(id, titile, content, category)와 일치하는지 FastAPI가 한 번 더 검증하여 불필요한 필드(next_id 등)의 응답 노출을 원천 차단합니다.
def list_knowledge():
    with LOCK:
        data = read_data()
    # BEGIN B-API-01
    # TODO B-API-01: data의 entries를 id 오름차순으로 반환하세요. sorted(..., key=lambda e:
    # e["id"])를 사용할 수 있습니다. next_id는 응답하지 않습니다.
    return sorted(data["entries"], key=lambda e: e["id"]) # data 딕셔너리에서  전체 메타데이터(next_id 등)를 제외하고 순수 목록 배열인 data["entries"]만 꺼내옵니다.
                                                          # 파이썬 내장 함수 sorted()와 lambda 식을 사용하여, 각 항목(e)의 고유 번호(e["id"])를 기준으로 작은 숫자부터 큰 숫자 순서(오름차순)로 안전하게 정렬된 새 리스트를 반환합니다.
    # END B-API-01
@app.get("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def get_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
    for entry in data["entries"]:
        # BEGIN B-API-02
        # TODO B-API-02: 반복 중인 entry의 id가 knowledge_id와 같을 때 entry를 반환하세요. 목록 인덱스와 ID를
        # 혼동하지 마세요.
        if entry["id"] == knowledge_id:
            return entry
        # END B-API-02
    raise HTTPException(404, "Knowledge not found")

@app.post("/api/knowledge", status_code=201, response_model=Knowledge)
def create_knowledge(payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        # BEGIN B-API-03
        # TODO B-API-03: payload를 dict로 변환하여 entry에 넣고, data의 next_id 값을 entry의 id로
        # 넣으세요.
        entry = payload.model_dump()
        entry["id"] = data["next_id"]
        # END B-API-03
        # BEGIN B-API-04
        # TODO B-API-04: entry를 entries에 추가하고 next_id를 1 늘린 뒤 write_data(data)로 저장하세요.
        data["entries"].append(entry)
        data["next_id"] += 1
        write_data(data)
        # END B-API-04
    return entry

@app.put("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def update_knowledge(knowledge_id: int, payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                updated = payload.model_dump()
                updated["id"] = knowledge_id
                # BEGIN B-API-05
                # TODO B-API-05: 찾은 위치 i의 항목을 updated로 교체한 뒤 저장하세요. 같은 ID를 유지하고 다른 항목은 변경하지
                # 않습니다.
                data["entries"][i] = updated
                write_data(data)
                # END B-API-05
                return updated
    raise HTTPException(404, "Knowledge not found")

@app.delete("/api/knowledge/{knowledge_id}", status_code=204)
def delete_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                # BEGIN B-API-06
                # TODO B-API-06: 찾은 위치 i의 항목 하나만 삭제하고 저장하세요. next_id는 줄이지 않습니다.
                data["entries"].pop(i)
                write_data(data)
                # END B-API-06
                return Response(status_code=204)
    raise HTTPException(404, "Knowledge not found")
