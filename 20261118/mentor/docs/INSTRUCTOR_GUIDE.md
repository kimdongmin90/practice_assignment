# 강사용 Day23 운영안 · 8교시 × 3수준

**수업 흐름:** 각 교시의 HTML 개념 설명 → `01_basic` 3 TODO → 학생 이해도에 따라 `02_intermediate` 5 TODO / `03_advanced` 6 TODO → 최종 결과 비교.
각 수준은 동일한 데이터·모델·DB 계약이며, 폴더 분리는 기능이 실제로 분리돼야 할 때만 추가합니다.

**연계:** 지식 101~103은 11/16~17 출력 계약과 연결하고 변경하지 않습니다. 104~109는 오늘 추가한 가상 검색 자료입니다.

**실습별 설명 초점:**

1. ID를 벡터 행과 혼동하지 않도록 ID/원문/버전→passage 문자열을 명시합니다. 기존 101~103은 고정합니다.
2. Dot/Cosine/L2의 계산 결과와 정렬 방향을 나란히 보고, 영벡터 오류를 숨기지 않습니다.
3. `query: `와 `passage: `는 E5의 역할별 입력 계약입니다. 384차원 출력과 512 토큰 길이는 다른 개념입니다.
4. PG 서버 확장 DLL 설치·현재 DB 활성화·Python 어댑터 등록은 각기 독립 단계입니다. 자주 발생하는 `transaction is aborted`를 바로 원래 오류로 역추적하게 합니다.
5. 실제 데이터/벡터는 같은 ID로 한 행에 저장하고, Cosine `<=>` 오름차순·category 조건·파라미터 바인딩을 확인합니다.
6. HNSW가 생성되어도 DB가 반드시 Index Scan을 택하지 않습니다. 9건에서 성능 일반화를 금합니다.
7. Top-k 후보가 존재해도 보관 기간 같은 속성이 없으면 답을 만들 수 없습니다. 정상 빈 결과/DB 장애/관련성 부족을 구분합니다.
8. 오늘은 Retriever의 원문 후보 반환까지입니다. Day25 RAG에서 실제 LLM 호출·출처 검증을 연결합니다.

**강사 검수 범위:**
- `python mentor/verification/verify_package.py`: 강사용 fixture 전체 실행, 수강생 TODO 장벽, HTML 데이터 일치 확인.
- `python -m pytest mentor/verification/test_local.py -q`: 수학·모의 검색·SQL·오류 계약 검사.
- fixture 통과는 실제 PostgreSQL 18.6/pgvector 0.8.7의 빌드 성공이나 실제 E5 다운로드 성공을 입증하지 못합니다.
- Windows 실기기 테스트는 PostgreSQL 확장 설치를 완료한 강사 PC에서 별도 실행해 기록합니다.

**안전한 배포:**
- `Day23_20261118_mentee.zip`만 학생에게 배포합니다.
- `mentor`의 정답 코드와 검증 스크립트, 과거 출력은 학생에게 배포하지 않습니다.
- 실제 `.env`, API 키, DB 비밀번호는 포함하지 않습니다.
