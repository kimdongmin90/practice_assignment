from pydantic import BaseModel, Field # Pydantic의 데이터 검증 및 직렬화 기능을 제공하는 최상위 부모 클래스를 BaseModel로 불러옵니다.
                                      # 각 변수에 최소/최대 길이, 기본값, 설명 등 세부 제약조건을 부여하는 함수를 Field로 불러옵니다.

# 코드 접근 방식 (3대 핵심 설계)

# 1. 입력(Write)과 출력(Read) 스키마의 명확한 분리
# 	데이터를 새로 생성하거나 수정할 때(KnowledgeWrite)는 사용자가 id 값을 임의로 보내지 못하도록 id 필드를 제외했습니다.
# 	반대로 DB에서 조회해 사용자에게 돌려줄 때(KnowledgeRead)는 DB가 자동 생성한 id를 포함하여 반환하도록 설계했습니다.
# 2. 클래스 상속을 통한 중복 코드 제거
# 	KnowledgeRead가 KnowledgeWrite를 상속받음으로써 title, content, category 속성과 길이 검증 규칙을 다시 적지 않고 깔끔하게 재사용했습니다.
# 3. DB 제약조건과의 완벽한 동기화 (Field)
# 	앞서 PostgreSQL에서 설정한 CHECK (char_length(title) BETWEEN 1 AND 80) 등의 DB 제약조건과 동일한 글자 수 제한(min_length, max_length)을 파이썬 코드 단에 먼저 배치하여, 잘못된 요청이 DB까지 도달하기 전에 FastAPI가 자동으로 422 Unprocessable Entity 에러로 차단하게 만듭니다.

# 1. 데이터 생성(POST) 및 수정(PUT) 요청 시 클라이언트가 보낼 데이터 규격
class KnowledgeWrite(BaseModel):
    title: str = Field(min_length=1, max_length=80) # title: 필수 문자열이며, 빈 문자열("") 방지를 위해 최소 1자, DB 컬럼 크기인 최대 80자까지 허용합니다.
    content: str = Field(min_length=1, max_length=2000) # content: 필수 문자열이며, 최소 1자 이상 최대 2,000자 이하의 본문 텍스트만 허용합니다.
    category: str = Field(min_length=1, max_length=30) # category: 필수 문자열이며, 최소 1자 이상 최대 30자 이하의 카테고리 이름만 허용합니다.

# 2. 데이터 조회(GET) 및 생성 완료 후 서버가 클라이언트에게 응답할 데이터 규격
class KnowledgeRead(KnowledgeWrite):
    id: int # 부모 클래스(KnowledgeWrite)의 3가지 필드를 모두 물려받은 상태에서 고유 식별자(id)만 추가합니다.
