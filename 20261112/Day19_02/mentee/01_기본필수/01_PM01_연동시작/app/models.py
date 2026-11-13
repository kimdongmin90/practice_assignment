from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Identity, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 전체 코드 접근 방식 (4대 핵심 설계)

# 1. DB 엔진 호환성을 고려한 가변 타입 설계 (with_variant)
# 	• 실무/실습 DB인 PostgreSQL에서는 대용량 처리를 위해 BIGINT를 쓰고, 가벼운 테스트/정적 검수 환경인 SQLite에서는 자동 증가 제약 때문에 INTEGER를 쓰도록 ID_TYPE을 유연하게 분리했습니다.
# 2. SQLAlchemy 2.0 최신 타입 힌트 매핑 (Mapped, mapped_column)
# 	• 파이썬의 타입 힌트(Mapped[int], Mapped[str])를 사용하여 에디터의 자동완성과 타입 검사를 완벽히 지원하도록 설계했습니다.
# 3. DB 수준 무결성 제약조건의 코드화 (__table_args__)
# 	• 테이블 이름(__tablename__)뿐만 아니라 글자 수 제한(CheckConstraint), 외래키 삭제 방지(ondelete="RESTRICT"), 자동 증가 키(Identity(always=True))를 모델 내부에 명시하여 DB 스키마와 파이썬 코드의 일관성을 맞췄습니다.
# 4. 양방향 객체 관계 탐색 (relationship & back_populates)
# 	• Category 객체에서 속해 있는 지식 목록(category.knowledge_items)을 바로 꺼내 볼 수 있고, 반대로 Knowledge 객체에서 부모 카테고리 정보(knowledge.category)를 점(.) 연산자로 즉시 참조할 수 있도록 양방향 연결을 구축했습니다.


# PostgreSQL에서는 BIGINT, SQLite 기반 정적 검수에서는 INTEGER가 되도록 정의합니다.
ID_TYPE = Integer().with_variant(BigInteger, "postgresql")

class Base(DeclarativeBase): # 모든 ORM 모델 클래스가 상속받아야 하는 SQLAlchemy 2.0 최상위 베이스 클래스입니다.
    pass

class Category(Base):
    __tablename__ = "categories" # 실제 DB에 생성/매핑될 테이블 이름입니다.
    __table_args__ = ( # 테이블 수준의 제약조건 설정(튜플 형태이므로 요소가 1개일 때 끝에 쉼표 필수)입니다.
        CheckConstraint("char_length(name) BETWEEN 1 AND 30", name="categories_name_length"),
    )
    id: Mapped[int] = mapped_column(ID_TYPE, Identity(always=True), primary_key=True) # Identity(always=True): PostgreSQL의 'GENERATED ALWAYS AS IDENTITY'와 동일한 자동 증가 기본키 설정입니다.
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    knowledge_items: Mapped[list["Knowledge"]] = relationship(back_populates="category") # 1:N 관계 설정(하나의 카테고리는 여러 개의 Knowledge 항목을 리스트로 가짐)합니다.
                                                                                         # back_populates="category": Knowledge 클래스의 'category' 속성과 양방향 동기화합니다.

class Knowledge(Base):
    __tablename__ = "knowledge"
    __table_args__ = ( # 제목(1~80자)과 본문(1~2000자) 길이 검증 제약조건을 앞서 작성한 SQL 명세와 동일하게 매핑합니다.
        CheckConstraint("char_length(title) BETWEEN 1 AND 80", name="knowledge_title_length"),
        CheckConstraint("char_length(content) BETWEEN 1 AND 2000", name="knowledge_content_length"),
    )
    id: Mapped[int] = mapped_column(ID_TYPE, Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column( # categories 테이블의 id를 참조하여 외래키(ForeignKey)를 설정하며 자식이 있을 때 부모 삭제(RESTRICT)를 차단합니다.
        ID_TYPE, ForeignKey("categories.id", ondelete="RESTRICT", name="knowledge_category_fk"), nullable=False
    )
    category: Mapped[Category] = relationship(back_populates="knowledge_items") # N:1 관계 설정(각 지식 데이터는 하나의 부모 Category 객체에 연결됨)합니다.
