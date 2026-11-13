from functools import lru_cache # 함수의 반환값을 메모리에 캐싱하여 재호출 시 즉시 돌려주는 성능 최적화 데코레이터입니다.
from sqlalchemy.engine import URL # SQLAlchemy가 데이터베이스에 접속할 때 사용하는 구조화된 연결 주소 객체입니다.
from pydantic_settings import BaseSettings, SettingsConfigDict # 환경 변수(.env)를 자동으로 읽어오는 Pydantic 설정 전용 부모 클래스로 BaseSettings를 사용합니다.
                                                               # .env 파일 경로, 인코딩, 추가 변수 처리 방식을 지정하는 설정 딕셔너리입니다.

# 전체 코드 접근 방식 (4대 핵심 설계)

# 1. 환경 변수 자동 매핑 및 검증 (BaseSettings)
# 	BaseSettings를 상속받으면 클래스 변수명(db_user, db_password 등)과 일치하는 대문자 환경 변수(DB_USER, DB_PASSWORD)를 .env 파일에서 자동으로 찾아 값을 덮어씁니다.
# 	만약 .env에 값이 없으면 미리 적어둔 기본값("postgres", 5432 등)을 사용하고, db_port처럼 타입이 int로 지정된 경우 문자열 "5432"를 읽어와도 숫자로 자동 형변환합니다.
# 2. 특수문자 안전한 URL 객체 조립 (URL.create)
# 	비밀번호에 @, #, / 같은 특수문자가 포함되면 일반 문자열 결합(f"postgresql://...") 시 파싱 에러가 발생합니다.
#   URL.create()를 사용하면 특수문자를 안전하게 인코딩한 URL 객체를 반환합니다.
# 3. 계산된 속성 제공 (@property)
# 	database_url을 함수 호출(settings.database_url())이 아닌 일반 변수(settings.database_url)처럼 깔끔하게 꺼내 쓸 수 있도록 프로퍼티로 설계했습니다.
# 4. 설정 객체 싱글톤 캐싱 (@lru_cache)
# 	요청이 들어올 때마다 .env 파일을 디스크에서 매번 다시 읽는 I/O 낭비를 막기 위해, get_settings() 호출 결과를 메모리에 한 번만 저장해 두고 재사용합니다.


class Settings(BaseSettings):
    db_user: str = "postgres" # .env 파일에 해당 키가 없을 때 사용할 기본 접속 정보(Fallback)와 자료형 정의입니다.
    db_password: str = "CHANGE_ME"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "day19_crud_b"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore") # 현재 폴더의 '.env' 파일을 UTF-8로 읽고, 클래스에 정의되지 않은 나머지 환경 변수는 에러 없이 무시(extra="ignore")합니다.

    @property # 메서드를 일반 변수(속성)처럼 'settings.database_url' 형태로 호출하게 해주는 파이썬 내장 데코레이터입니다.
    def database_url(self) -> URL:
        # 비밀번호를 URL 문자열로 직접 이어 붙이지 않고 URL.create가 인코딩을 맡습니다.
        # TODO B01: DB 설정값으로 PostgreSQL+psycopg URL 객체를 반환하세요.
        return URL.create( # SQLAlchemy 엔진이 인식할 수 있는 구조화된 연결 URL 객체를 안전하게 생성하는 클래스 메서드입니다.
                           # PostgreSQL 3버전 드라이버('postgresql+psycopg')와 각 설정값을 결합해 안전한 URL 객체 생성합니다.
            drivername="postgresql+psycopg", # 사용할 데이터베이스 종류(postgresql)와 파이썬 DB 드라이버(psycopg)를 '+'로 연결해 지정합니다.
            username=self.db_user, # 사용할 데이터베이스 종류(postgresql)와 파이썬 DB 드라이버(psycopg)를 '+'로 연결해 지정합니다.
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

@lru_cache # 애플리케이션 전체에서 Settings 인스턴스를 단 한 번만 초기화하여 공유하기 위한 싱글톤 팩토리 함수입니다.
def get_settings() -> Settings:
    return Settings()
