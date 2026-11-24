# 11/24 수업 정리: LangChain RAG & Reranking

> **주제:** Query Rewrite · Multi-query · Cross-Encoder를 활용한 검색 품질 고도화 및 파이프라인 통합

---

## 🧭 전체 파이프라인 흐름 한눈에 보기

단순 벡터 검색(Naive RAG)의 한계인 **'검색 전 실패(모호한 질문)'**와 **'검색 후 실패(정답 문서의 낮은 순위)'**를 해결하기 위해 파이프라인을 5단계로 고도화합니다.

```text
[1. 입력 준비 (State 보존)] 
  └─ 원 질문(question)과 대화 이력(history)을 훼손 없이 보존
       │
       ▼
[2. 검색 전 개선: Query Rewrite & Multi-query] 
  ├─ Rewrite: 대명사/생략된 맥락을 복원해 독립형 검색 질문 생성 ("그거 취소는?" → "회의실 예약 취소 절차는?")
  └─ Multi-query: 다양한 관점의 질문을 확장 생성하여 검색 재현율(Recall) 향상 (사용된 chunk_id JSON 기록)
       │
       ▼
[3. 1차 후보 검색 & 접근 제어 (Bi-Encoder + Access Control)]
  ├─ 권한 필터링(Pre/Post-filtering)으로 조회 가능한 문서 범위 제한
  └─ Bi-Encoder(Vector DB)로 대규모 문서 중 상위 후보(Top-K, 예: 10개) 고속 추출
       │
       ▼
[4. 2차 정밀 재순위화 (Cross-Encoder Reranking)]
  └─ [질문, 문서] 쌍을 함께 입력해 정밀 점수 산출 → 토큰 절약 및 정확도를 위해 최상위 Top-1~3 선별
       │
       ▼
[5. 통합 및 진단 (Integration & Diagnose)]
  ├─ Context Builder 연결 (원 질문 유지 + JSON 출처 보존)
  └─ Golden Set(정답 데이터) 기준으로 변수를 1개씩 변경하며 성능 비교·진단
```

---

## 1. LangChain RAG Orientation

### 1.1 핵심 구성 요소
* **LangChain:** Prompt, Model, Retriever, Tool 등의 입출력을 공통 인터페이스로 연결하는 Python 개발 라이브러리 (맞춤형 파이프라인 하네스 제공).
* **RunnableLambda:** 일반 Python 함수를 LangChain의 `Runnable` 실행 단위로 감싸는 클래스 (커스텀 전처리·검색 함수를 Chain에 연결할 때 사용).
* **`|` (LCEL, LangChain Expression Language):** 왼쪽 `Runnable`의 출력을 오른쪽 `Runnable`의 입력으로 연결하는 파이프 연산자. *(주의: 식을 조립하는 것만으로 실행되지 않음)*
* **`invoke()`:** 조립된 `Runnable`이나 `Chain`에 실제 입력을 넣어 순차 실행을 트리거하는 메서드.

### 1.2 Chain 내부 데이터(State) 이동 흐름
1. **입력 준비 (`prepare`):**
   * `<INPUT>` 사용자 질문 문자열 $\rightarrow$ `<OUTPUT>` `state = {"question": ...}`
   * `invoke()` 호출 시 첫 번째 `Runnable`로 딕셔너리가 전달됨.
2. **질문 정제 (`clean_question`):**
   * `<INPUT>` `state["question"]` $\rightarrow$ `<OUTPUT>` `{"question": ..., "search_query": ...}`
   * **원 질문을 보존**하면서 검색용 공백 제거 등 기초 정제 수행.
3. **단계 설명 (`explain_step`):**
   * `<INPUT>` `state["search_query"]` $\rightarrow$ `<OUTPUT>` `"Retriever 입력: 회의실 예약 취소 절차는?"`

### 1.3 검색 실패 유형과 설계 시 관찰 포인트
* **검색 전 실패:** *"그것도 가능해?"*처럼 대상이 빠진 질문은 임베딩하기 전에 맥락을 복원해야 함. (이전 `history`를 어디까지 참조할지 범위 설정이 중요)
* **검색 후 실패:** 정답 문서가 Top-10 후보에는 들었으나 9위라면, LLM Context(Top-3)에서 누락됨 $\rightarrow$ **Reranking**으로 순위를 끌어올려야 함(토큰 절약 효과).
* **설계 균형:** Chain을 잘게 나눌수록 유지보수와 중간 값 확인이 쉽지만, 코드 복잡도가 올라가므로 적절한 균형이 필요함.

> **시연 및 디버깅 4대 체크리스트**
> 1. **질문 문제:** 대명사·생략된 대상을 검색 전에 복원했는가?
> 2. **후보 문제:** 원문이 현재 버전·Category·권한 필터 조건으로 검색 가능한 상태인가?
> 3. **순위 문제:** 후보군 안에 정답 문서가 존재하는지 먼저 확인한 후 Rerank를 수행하는가?
> 4. **오류 분류:** LLM 생성 오류나 API 인증 오류는 검색 알고리즘 수정으로 해결되지 않으므로 원인을 분리해 진단해야 함.

---

## 2. Conversational Query Rewrite

* **개념:** 사용자의 모호하거나 불완전한 질문을 검색 엔진(Vector DB)이 정확히 이해할 수 있도록 **명확한 독립형 질문(Standalone Question)**으로 재작성하는 기법.
* **주요 활용:**
  * **대화 맥락 복원 (Conversational Rewrite):** 이전 대화 이력(`history`)을 참고해 대명사("그거", "이것")나 생략된 주어를 구체화.
  * **검색 최적화 (Retrieval Optimization):** 구어체나 추상적 표현을 문서 검색에 유리한 핵심 키워드 형태로 다듬음.
* **설계 원칙:** 입력 단계에서는 `원 질문`과 `history`를 원본 그대로 보존하고, 검색용 질문 생성(Rewrite)은 Chain 내부에서 수행함. *(필요시 재작성된 질문에 대해서도 검증/재순위화 진행)*

---

## 3. Expansion & Multi-query

* **개념:** 하나의 질문을 여러 관점의 유사 질문들로 확장하여 검색 누락(Recall 부족)을 줄이는 기법.
* **구현 방법 3가지:**
  1. **LLM Temperature 상향:** 생성 다양성을 높여 여러 표현의 질문을 유도.
  2. **Prompt Engineering:** *"이 질문을 다른 관점에서 3가지로 다시 작성해 줘"*와 같이 프롬프트로 지시.
  3. **Vector DB 엔지니어링:** 다중 쿼리 결과를 병합(Fusion)하고 중복을 제거하는 검색 로직 구성.
* **운영 및 검증 주의사항:**
  * **이력 추적:** Multi-query 수행 시 어떤 질문에서 어떤 `chunk_id`가 검색되었는지 **JSON 형태로 기록**을 남겨야 함.
  * **품질 검증:** Multi-query가 항상 성능을 높이는 것은 아니며 노이즈를 섞어 품질을 떨어뜨릴 수도 있으므로, **사람이 직접 결과를 검수**해야 함 (시간 소요가 큼).

---

## 5. Cross-Encoder Reranking & 접근 제어

### 5.1 Bi-Encoder vs Cross-Encoder 비교

| 구분 | Bi-Encoder (1단계 후보 검색) | Cross-Encoder (2단계 정밀 재순위화) |
| :--- | :--- | :--- |
| **입력 형태** | 질문(`Question`), 문서(`Document`)를 **각각 분리**하여 입력 | `[CLS] 질문 [SEP] 문서 [SEP]` **쌍(Pair)으로 합쳐서** 입력 |
| **출력 결과** | 각 텍스트의 **임베딩 벡터 (Vector)** | 두 문장 간의 **관련성 점수 (Score, 0~1)** |
| **사전 계산** | **가능** (문서 벡터를 Vector DB에 미리 저장) | **불가능** (질문이 들어올 때마다 실시간 쌍 계산 필요) |
| **추론 속도** | 매우 빠름 (수백만 건 대규모 검색에 유리) | 느림 (후보 수십 건 수준에 적합) |
| **검색 정확도** | 보통 (전반적인 의미 유사도 측정) | 매우 높음 (질문-문서 단어 간 세밀한 상호작용 파악) |
| **RAG 역할** | **Candidate Retrieval (Retriever)** | **Reranking (Reranker)** |

### 5.2 접근 제어(Access Control) 구현 함수 4종

사용자 권한에 따라 허용된 문서만 검색·제공하기 위해 파이프라인 역할별로 구현하는 함수 체계입니다.

1. **사용자 권한 추출 및 검증 함수**
   * `get_user_permissions(user)` / `extract_user_context(request)`
   * **역할:** 토큰이나 프로필에서 역할(`role`), 부서(`dept`), 보안 등급(`clearance_level`) 추출.
   * **예시:** `{"user_id": "u101", "role": "staff", "dept": "sales"}`
2. **검색 필터 조건 생성 함수 (Metadata Filter Builder)**
   * `build_access_filter(user_context)` / `create_metadata_filter(role)`
   * **역할:** 사용자 권한을 Vector DB가 이해할 수 있는 메타데이터 필터 쿼리로 변환.
   * **예시:** `{"access_level": {"$lte": 1}}` 또는 `{"allowed_roles": {"$in": ["staff", "all"]}}`
3. **개별 문서 권한 판별 함수 (Authorization Check)**
   * `is_authorized(user, doc)` / `can_access_doc(user_role, doc_metadata)`
   * **역할:** 특정 문서 1건에 대해 사용자의 열람 가능 여부를 `True / False`로 반환 (2차 검증용).
4. **권한 기반 문서 필터링 및 마스킹 함수**
   * `filter_accessible_docs(docs, user)`: `is_authorized()`를 순회 적용해 권한 있는 문서 리스트만 반환.
   * `redact_sensitive_info(text, user)` *(선택)*: 문서는 볼 수 있으나 민감 필드(주민번호, 급여 등) 권한이 없을 때 `***`로 마스킹 처리.

---

## 6. LangChain Integration (파이프라인 통합)

* **Context Builder 연결:** 앞선 단계(Rewrite $\rightarrow$ Multi-query $\rightarrow$ 접근 제어 $\rightarrow$ Retrieval $\rightarrow$ Cross-Encoder Reranking)를 거쳐 선별된 최종 문서들을 LLM 프롬프트용 Context 문자열로 조립합니다.
* **원 질문 유지 및 출처 보존:** 최종 답변 생성 단계에서도 사용자의 **원 질문(Original Question)**을 잃어버리지 않고 전달하며, 근거로 사용된 문서의 메타데이터와 출처를 **JSON 형식으로 보존**하여 추적 가능하게 만듭니다.

---

## 7. Compare & Diagnose (비교 및 진단)

* **통제 변인 원칙 (1개씩 변경):** 검색 파이프라인을 개선할 때는 머신러닝 하이퍼파라미터 튜닝과 마찬가지로 **반드시 조건을 한 번에 1개씩만 변경**해야 어떤 기법(Rewrite, Multi-query, Rerank 등)이 성능 변화를 일으켰는지 정확히 원인을 파악할 수 있습니다.
* **Golden Set (정답 데이터셋):**
  * 평가의 기준이 되는 **불변의 정답 질문-문서-답변 데이터셋**(`gold`, `gold set`, `golden set`)을 구축해 두고, 파이프라인 변경 전후의 검색 정확도(Recall@K, MRR 등)를 객관적으로 비교·진단합니다.