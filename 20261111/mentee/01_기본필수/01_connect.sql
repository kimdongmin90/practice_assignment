-- Day18 | 실습 01: 접속과 첫 SQL | PPT 7~13, 68, 78~80 | 30분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)
-- @step은 실행 단위를 표시하는 주석입니다. SQL 명령이 아닙니다.
-- 한 @step 구간씩 선택 실행합니다. 오류 뒤 ROLLBACK은 반드시 별도 실행합니다.
-- __TODO_...__는 구현할 빈칸, __NEW_ID__/__A_ID__/__B_ID__/__C_ID__는 실제 실행 입력입니다.
-- 입력 ID는 RETURNING에서 읽어 해당 토큰을 실제 정수로 바꿉니다. 4·5·6으로 예측하지 않습니다.
-- 아직 남은 토큰 때문에 생긴 문법 오류는 의도한 제약 실패로 인정하지 않습니다.

-- @step E1_GUARD expect=00000 capture=- reconnect=false
-- 제공된 안전 확인입니다. 이 블록은 TODO가 아닙니다.
-- 개인 수업용 DB에서만 실행합니다. 이름만 맞다고 운영 DB가 안전해지는 것은 아닙니다.
DO $guard$ -- PostgreSQL에서 익명 코드 블록(Procedural Language)을 실행하는 명령어로 별도의 저장 프로시저를 만들지 않고 즉석에서 PL/pgSQL(절차형 문법) 제어문을 수행할 때 감싸는 식별자입니다.
BEGIN -- DO 블록의 실제 실행 로직이 시작됨을 알리는 선언문입니다.
  IF current_database() !~ '^knowledge_lab(_[a-z0-9_]+)?$' THEN -- 현재 접속한 DB 이름이 요구 조건에 맞는지 정규표현식(~ 로직)으로 정밀 검사합니다.
                                                                -- '^knowledge_lab(_[a-z0-9_]+)?$' 규칙을 통해 'knowledge_lab' 또는 뒤에 언더바와 문자가 붙은 실습용 DB가 아니면 조건문(IF)이 발동합니다.
    RAISE EXCEPTION '개인 knowledge_lab DB에 다시 접속하세요. 현재 DB: %', current_database(); -- # 실행을 즉시 중단하고 클라이언트에게 강제로 빨간색 에러 메시지를 던지는 명령으로 잘못된 DB(예: 기본 postgres DB)에 연결된 상태로 실습하여 과제 데이터가 꼬이는 것을 원천 차단합니다.
                                                                                           -- % 자리에 실제 DB명이 매핑됩니다.
  END IF; -- IF 조건문 블록의 종료를 선언합니다.
END; -- DO 블록의 로직 종료 선언합니다.
$guard$; -- 익명 블록의 끝을 닫고 세미콜론(;)으로 이 구문을 완전히 마무리합니다.
SET search_path TO public; -- 스키마(Schema) 탐색 경로를 'public'으로 기본 지정하는 스크립트 명령어로 테이블 조회 시 앞에 스키마명(예: public.users)을 매번 붙이지 않아도 자동으로 기본 public 공간을 찾도록 강제합니다.

-- @step E1_PING expect=00000 capture=- reconnect=false -- @step E1_PING: 자동 채점 시스템(예: 멘토링/실습 플랫폼의 과제 검사기)이 인식하는 단계 구별용 주석 태그이며 expect=00000(성공 응답 대기), capture=-(결과 덤프 제외), reconnect=false(연결 유지) 설정을 자동 검사기에 전달합니다.
SELECT 1 AS connected; -- 데이터베이스와 네트워크 통신이 끊어지지 않고 정상적으로 붙어있는지 확인하기 위한 더미(Dummy) 조회이며, 1이라는 상수를 `connected`라는 이름의 컬럼으로 출력하여 세션 살아있음을 단순 테스트(Ping)합니다.

-- @step E1_DB expect=00000 capture=- reconnect=false
-- BEGIN TASK B01_01
-- TODO B01_01
-- 현재 연결한 DB 이름을 반환하는 함수를 넣으세요. 기대 이름은 knowledge_lab입니다.
-- 힌트: current_database(). 이 명령은 새 DB에 접속하는 명령이 아닙니다.
SELECT current_database() AS database_name; -- current_database() 내장 함수로 PostSQL 내부에서 현재 세션에 붙어 있는 데이터베이스명을 동적으로 꺼내옵니다.(PostgreSQL 시스템에 실시간 접속 중인 카탈로그(DB) 이름을 텍스트로 반환하는 기본 내장 함수)
                                            -- 출력되는 결과 창의 컬럼 이름을 기대 이름인 knowledge_lab으로 치환(Alias)해 주는 문법입니다.
                                            -- 데이터베이스 자가 진단(Health Check) 쿼리로 사용하여 현재 내가 요구되는 올바른 공간(`knowledge_lab`)에서 실습하고 있는지 검증값을 반환합니다.
-- END TASK B01_01

-- @step E1_INFO expect=00000 capture=- reconnect=false
SELECT current_user AS user_name, version() AS server_version; -- current_user 내장 환경 변수로 현재 데이터베이스 세션을 열고 로그인한 계정명(Role)을 반환합니다.
                                                               -- version() 내장 함수로 설치된 PostgreSQL 데이터베이스의 상세 커널 버전 및 빌드 운영체제 정보를 문자열로 리턴하여 시스템 모니터링이나 인프라 감사용 쿼리로 주로 쓰이며, 여기서는 학생의 로그인 정보와 서버 상태를 조회합니다.

-- @step E1_ENCODING expect=00000 capture=- reconnect=false
SHOW client_encoding; -- 현재 데이터베이스 서버와 클라이언트(DBeaver, Git Bash 등) 간의 문자 인코딩 설정을 화면에 출력하는 명령어로 한글이나 유니코드 데이터가 깨지지 않고 전달되는지 서버 환경 변수(예: UTF8 등)를 확인하는 용도입니다.
SELECT '한글 연결 확인' AS korean_text; -- 데이터베이스 연결 채널을 통해 실제 다국어(한글) 문자열 데이터가 손상 없이 온전하게 입출력되는지 최종 문자 테스트해 '한글 연결 확인'이라는 한글 리터럴을 `korean_text`라는 이름의 단일 셀 결과물로 화면에 뿌려 출력 인코딩을 검증합니다.
