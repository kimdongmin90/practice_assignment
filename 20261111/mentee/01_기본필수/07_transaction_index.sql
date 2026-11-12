-- Day18 | 실습 07: 취소·확정·인덱스·실행계획 | PPT 48~54, 76 | 30분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)
-- @step은 실행 단위를 표시하는 주석입니다. SQL 명령이 아닙니다.
-- 한 @step 구간씩 선택 실행합니다. 오류 뒤 ROLLBACK은 반드시 별도 실행합니다.
-- __TODO_...__는 구현할 빈칸, __NEW_ID__/__A_ID__/__B_ID__/__C_ID__는 실제 실행 입력입니다.
-- 입력 ID는 RETURNING에서 읽어 해당 토큰을 실제 정수로 바꿉니다. 4·5·6으로 예측하지 않습니다.
-- 아직 남은 토큰 때문에 생긴 문법 오류는 의도한 제약 실패로 인정하지 않습니다.

-- @step E7_GUARD expect=00000 capture=- reconnect=false
-- 제공된 안전 확인입니다. 이 블록은 TODO가 아닙니다.
-- 개인 수업용 DB에서만 실행합니다. 이름만 맞다고 운영 DB가 안전해지는 것은 아닙니다.
DO $guard$ --PostgreSQL에서 익명 절차형 블록(PL/pgSQL 코드)을 선언하고 실행하는 명령어로 별도로 저장 함수를 빌드하지 않고, 조건문이나 예러 발생 제어를 즉석에서 가동할 때 식별자 $guard$로 감싸 실행합니다.
BEGIN -- # DO 블록이 제어할 실제 실행 로직의 시작점을 선언합니다.
  IF current_database() !~ '^knowledge_lab(_[a-z0-9_]+)?$' THEN -- 실습 진행 전, 엉뚱한 기본 DB(예: postgres)에서 데이터가 수정되어 오염되는 것을 완벽히 방지하는 안전장치로 내장 함수 `current_database()`의 결과물이 정규표현식 규칙에 맞지 않으면 예외 처리 조건문(IF) 내부로 진입합니다.
    RAISE EXCEPTION '개인 knowledge_lab DB에 다시 접속하세요. 현재 DB: %', current_database(); -- 실행을 그 자리에서 즉시 강제 중단하고 에러 메시지를 화면에 출력하는 명령어로, 잘못된 연결일 때 % 자리에 현재 접속 중인 잘못된 DB 명을 박아서 개발자에게 알려주고 튕겨냅니다.
  END IF; -- 앞서 시작된 IF 조건문 블록의 끝을 명시합니다.
END; -- DO 실행 블록의 완전한 마감 선언합니다.
$guard$; -- 커스텀 가드 블록을 종료하고 세미콜론(;)으로 이 구문을 완전히 끝마칩니다.
SET search_path TO public; -- 현재 데이터베이스 세션에서 테이블을 찾을 기본 검색 스키마 경로를 'public'으로 지정하며 테이블 조회 시 앞에 스키마명(예: public.knowledge)을 붙이지 않고 그냥 `knowledge`라고만 적어도 알아서 물리 테이블을 찾도록 고정합니다.

-- 1. 데이터 수정 전 초기 상태 조회 및 트랜잭션 시작 구역
-- @step E7_BEFORE expect=00000 capture=- reconnect=false
SELECT id,content FROM public.knowledge WHERE id=2; -- 데이터를 조회하는 기본 쿼리 문법으로 WHERE id=2 제약 조건을 걸어 고유 식별 번호(ID)가 2번인 지식 데이터의 현재 본문(`content`) 원본 상태를 미리 화면에 출력하여 확인합니다.

-- @step E7_CANCEL_BEGIN expect=00000 capture=- reconnect=false
BEGIN; --데이터베이스 내에서 하나의 논리적 작업 단위인 트랜잭션(Transaction)을 정식으로 시작하겠다는 명령어로 이 명령이 떨어진 시점부터 일어나는 모든 추가, 수정, 삭제 연산은 메모리에만 임시 저장되며, `COMMIT`을 날리기 전까지 다른 사용자에게 보이지 않고 확정되지 않습니다.(안전하게 취소할 기회를 확보함)

-- 2. 1차 데이터 수정 작업 (RETURNING 절의 활용)
-- @step E7_TEMP expect=00000 capture=- reconnect=false
UPDATE public.knowledge SET content='취소할 임시 안내입니다.' WHERE id=2 RETURNING id,content; -- 특정 테이블의 특정 컬럼 값을 새 데이터로 변경하는 DML 명령어 'UPDATE public.knowledge SET...'으로 WHERE id=2를 타깃으로 잡고 해당 행의 content 값을 '취소할 임시 안내입니다.'라는 문자열로 변경합니다.
                                                                                            -- PostgreSQL만의 문법 'RETURNING id, content'으로, 수정 처리가 물리적으로 일어나자마자 변경이 완료된 최종 행(Row) 데이터를 그 자리에서 바로 SELECT 하듯 화면에 리턴해 줍니다.
                                                                                            -- 백엔드 코드와 연동할 때 굳이 SELECT를 다시 날리지 않고도 "내가 방금 수정한 결과물 데이터"를 한 번에 검증 및 활용할 수 있게 만듭니다.

-- 3. 트랜잭션 롤백(취소) 및 데이터 검증 구역
-- @step E7_CANCEL expect=00000 capture=- reconnect=false
-- BEGIN TASK B07_01
-- TODO B07_01
-- 임시 본문 수정을 확정하지 않고 취소하는 명령을 넣으세요. 다음 SELECT에서 시작 본문이 보여야 합니다.
ROLLBACK; -- 현재 열려 있던 트랜잭션 내의 모든 임시 변경 사항을 전면 취소하고 원래 상태로 되돌리는 명령어로 이전 라인에서 실행했던 '취소할 임시 안내입니다.' 수정 내역을 실시간 반영하지 않고 깔끔하게 무효화합니다.
-- END TASK B07_01

-- 4. 중간 상태 검증 및 2차 트랜잭션 수립 구역
-- @step E7_CANCEL_READ expect=00000 capture=- reconnect=false
SELECT id,content FROM public.knowledge WHERE id=2; -- 위의 UPDATE문이 현재 세션(트랜잭션) 안에서 의도한 대로 잘 박혔는지 다시 한번 직접 확인하기 위한 중간 모니터링 조회 명령어로 ID가 2번인 행을 다시 조회하여 방금 입력한 '취소할 임시 안내입니다.'가 안전하게 잘 보이는지 눈으로 검증합니다.

-- 5. 새 트랜잭션 시작 구역
-- @step E7_SAVE_BEGIN expect=00000 capture=- reconnect=false
BEGIN; -- 새로운 두 번째 트랜잭션을 수립하거나 기존 변경의 연장선상에서 논리적 작업 단위를 한 번 더 명시하며 일부 툴이나 DB 환경에서 앞선 트랜잭션이 아직 마감(`COMMIT` 이나 `ROLLBACK`)되지 않은 채로 또 BEGIN을 호출하면 경고(Warning)가 뜨거나 하위 트랜잭션(Savepoint 형식)으로 동작하게 됩니다.
       -- 실습 구조상 새로운 변경 흐름을 여는 단계이며 이 시점부터 발생하는 데이터 변경 동작은 `COMMIT`이 선언되기 전까지 임시 보관 상태가 됩니다.

-- 6. 2차 최종 데이터 수정 및 최종 확정 작업
-- @step E7_SAVE expect=00000 capture=- reconnect=false
UPDATE public.knowledge SET content='실행 전에 가상환경을 확인합니다.' WHERE id=2 RETURNING id,content; -- 지식 데이터를 최종 원하는 목적값으로 다시 덮어쓰는 과정으로 ID가 2번인 행을 최종 타깃으로 잡아 content 내용을 원래 의도했던 안내 문구인 '실행 전에 가상환경을 확인합니다.'로 완전 갱신합니다.
                                                                                                   -- 마찬가지로 RETURNING 절이 뒤에 붙어 있어, 바뀐 뒤의 데이터인 2번 ID와 변경 완료 문구를 쿼리 결과 탭에 즉각 되돌려줍니다.
                                                                                                   -- content 필드를 '실행 전에 가상환경을 확인합니다.'로 수정하고, `RETURNING` 절을 통해 바뀐 결과 행을 그 즉시 반환받아 모니터링합니다.

-- @step E7_COMMIT expect=00000 capture=- reconnect=false
-- BEGIN TASK B07_02
-- TODO B07_02
-- 가상환경 확인 안내를 확정하세요. 이 명령 후 새 연결에서 조회해도 같은 본문이 나와야 합니다.
COMMIT; -- 현재 트랜잭션 내부에서 수행한 모든 임시 변경 사항을 데이터베이스 물리 파일에 완전히 영구 기록(확정)하는 명령어로 이 명령을 실행함으로써 2번 데이터의 수정본이 확정되며, 이제 다른 사용자나 세션에서도 바뀐 본문을 볼 수 있게 됩니다.
-- END TASK B07_02

-- 7. 저장소 자가 진단 및 데이터 최종 상태 확인 구역
-- @step E7_RECONNECT expect=00000 capture=- reconnect=true
SELECT current_database() AS database_name; -- 현재 사용 중인 데이터베이스 카탈로그 명을 반환하는 내장 함수 current_database()로 'database_name'이라는 깔끔한 별칭으로 현재 세션이 `knowledge_lab` 데이터베이스에 정확히 머물고 있는지 자가 진단합니다.
SELECT id,content FROM public.knowledge WHERE id=2; -- 트랜잭션 커밋(`COMMIT`) 절차가 안전하게 끝나 물리 디스크에 안착했는지 데이터 최종 모니터링하여 2번 데이터를 재조회하여 최종 확정된 문구인 '실행 전에 가상환경을 확인합니다.'가 올바르게 찍히는지 검증합니다.

-- 8. 메타데이터 조회 및 데이터베이스 인덱스(Index) 성능 튜닝 구역
-- @step E7_INDEX_INSPECT expect=00000 capture=- reconnect=false
SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='public' AND tablename='knowledge' ORDER BY indexname; -- PostgreSQL 시스템 카탈로그 뷰인 `pg_indexes`에서 인덱스 정보를 탐색하는 메타 쿼리 'SELECT ... FROM pg_indexes' 명령어로 public 스키마 내의 `knowledge` 테이블에 정의된 모든 인덱스 이름(`indexname`)과 인덱스 생성 구문(`indexdef`)을 이름순으로 정렬해 현재 상태를 조회합니다.(기본적으로 PK 인덱스만 존재할 것입니다.)

-- @step E7_PLAN_BEFORE expect=00000 capture=- reconnect=false
EXPLAIN SELECT id,title FROM public.knowledge WHERE category_id=1; -- PostgreSQL 옵티마이저가 쿼리를 실행할 때 사용할 구조적 '실행 계획(Execution Plan)'을 예측하여 출력하는 명령 'EXPLAIN SELECT ...'로 category_id가 1인 데이터를 찾을 때, 인덱스가 없어 테이블 처음부터 끝까지 전체를 다 뒤지는 **Sequential Scan(Full Table Scan)** 현상을 눈으로 먼저 진단하는 접근 방식입니다.

-- 같은 이름이 이미 있으면 정의를 확인하고 CREATE 구간을 건너뜁니다.

-- @step E7_INDEX_CREATE expect=00000 capture=- reconnect=false
CREATE INDEX idx_knowledge_category_id ON public.knowledge(category_id); -- 데이터 검색 속도를 비약적으로 상승시키기 위해 특정 컬럼에 인덱스(색인)를 생성하는 명령어 'CREATE INDEX idx_knowledge_category_id ON ...'로 `knowledge` 테이블의 `category_id` 외래키 컬럼을 기반으로 `idx_knowledge_category_id`라는 B-Tree 구조의 탐색 인덱스를 물리적으로 구축합니다.

-- @step E7_PLAN_AFTER expect=00000 capture=- reconnect=false
EXPLAIN (ANALYZE, BUFFERS) SELECT id,title FROM public.knowledge WHERE category_id=1; -- 예측을 넘어 쿼리를 **실제 실행**해 보고, 소요된 밀리초(ms) 시간과 디스크 메모리 버퍼 활용량을 정밀 분석(Profiling)해 주는 고급 명령어 'EXPLAIN (ANALYZE, BUFFERS) SELECT ...'로 방금 만든 인덱스 덕분에 검색 방식이 **Bitmap Index Scan** 또는 **Index Scan**으로 효율적으로 전환되었는지, 그리고 자원 소모량이 얼마나 극적으로 줄었는지 성능 개선 결과(튜닝 성공 여부)를 수치로 증명합니다.

-- @step E7_FINAL expect=00000 capture=- reconnect=false
SELECT id, title, content, category_id FROM public.knowledge ORDER BY id; -- 인덱스 튜닝 및 데이터 수정 실습이 모두 끝난 뒤, 데이터의 무결성과 최종 정렬 상태를 리포트 형태로 확인하는 마감 조회를 통해 모든 데이터의 ID, 제목, 본문, 카테고리 ID 컬럼을 한눈에 볼 수 있도록 정렬하여 출력하면서 스크립트를 종료합니다.
