from functools import lru_cache
from contextlib import contextmanager
from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from app.settings import get_settings


# 전체 코드 접근 방식 (4대 핵심 설계)

# 1. 싱글톤 패턴을 통한 커넥션 풀(Connection Pool) 최적화 (@lru_cache)
# 	DB 엔진(Engine)과 세션 팩토리(sessionmaker)는 비용이 큰 객체이므로 요청이 들어올 때마다 새로 만들면 서버가 느려집니다.
#   @lru_cache를 붙여 애플리케이션 실행 중 단 한 번만 생성하고 메모리에 캐싱해 재사용합니다.
# 2. 의존성 주입(DI)을 통한 안전한 세션 생명주기 관리 (get_db & yield)
# 	FastAPI의 Depends(get_db)와 함께 쓰기 위한 제너레이터 함수입니다.
#   API 요청이 들어올 때 DB 세션을 하나 열어주고, 응답이 끝나면 에러 여부와 상관없이 with 블록을 빠져나오며 세션을 안전하게 닫아(close) 메모리 누수를 방지합니다.
# 3. 원자적(Atomic) 쓰기 작업을 보장하는 명시적 트랜잭션 (@contextmanager)
# 	데이터 생성, 수정, 삭제 중 중간에 에러가 터졌을 때 일부만 반영되는 불상사를 막기 위해 try ... except로 감싸서 성공 시에만 commit(), 실패 시 자동 rollback()되도록 경계를 묶었습니다.
# 4. 서버 기동 및 헬스체크용 자가 진단 (check_database)
# 	SQLAlchemy의 text() 구문을 이용해 실제 PostgreSQL 엔진에 순수 SQL 쿼리를 날려, 현재 연결된 DB명과 사용자 계정이 올바른지 런타임에 즉시 검증합니다.


# 엔진 및 세션 팩토리 초기화
@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    if settings.db_password == "CHANGE_ME": # 보안 및 초기 설정 누락 방지: 기본 비밀번호 그대로 실행하는 것을 원천 차단합니다.
        raise RuntimeError(".env의 DB_PASSWORD를 실제 학습용 비밀번호로 바꾸세요.")
    return create_engine(settings.database_url, pool_pre_ping=True) # 'pool_pre_ping=True' 명령어로 DB에 쿼리를 날리기 전 연결이 살아있는지 핑(Ping)을 먼저 쏴서 끊어진 커넥션 에러 예방합니다.

@lru_cache
def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False) # 'autoflush=False' 명령어로 개발자가 의도하지 않은 시점에 임시 데이터가 DB로 날아가는 현상 방지
                                                                                    # commit() 함수 사용 이후에도 메모리상의 파이썬 객체 속성을 에러 없이 계속 읽을 수 있도록 유지하기 위해 'expire_on_commit=False' 명령어를 사용합니다.

# FastAPI 라우터 연동용 세션 공급기
def get_db() -> Generator[Session, None, None]:
    # TODO B02: 요청마다 Session을 열어 yield하고 요청이 끝나면 닫히게 하세요.
    factory = get_session_factory()
    with factory() as session: # with 컨텍스트 매니저를 사용해 라우터 함수가 종료되면 자동으로 session.close() 함수로 호출합니다.
        yield session


# 트랜잭션 안전 래퍼
@contextmanager
def transaction(db: Session):
    """한 쓰기 요청의 flush와 commit을 같은 경계로 묶습니다."""
    try:
        yield # with transaction(db): 블록 내부의 비즈니스 로직(INSERT/UPDATE 등) 실행합니다.
        db.commit() # 모든 로직이 에러 없이 통과하면 DB에 영구 확정합니다.
    except Exception:
        db.rollback() # 단 하나라도 에러가 나면 변경 사항 전면 취소합니다.
        raise         # 발생한 에러를 FastAPI 예외 처리기로 다시 던집니다.

# DB 연결 상태 검증 함수
def check_database() -> tuple[str, str]:
    with get_engine().connect() as conn:
        row = conn.execute(text("SELECT current_database(), current_user")).one() # SQLAlchemy 2.0 표준 방식으로 순수 SQL 문자열은 반드시 text()로 감싸서 실행합니다.
                                                                                  # .one(): 결과가 정확히 1행(Row)임을 보장하며 추출합니다.
        return str(row[0]), str(row[1])
