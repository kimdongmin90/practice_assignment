"""Day23 실습 08 · AI Agent용 Retriever (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
# 준비물 챙기기(도구 상자 불러오기)
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / 'common')) # common 폴더에 있는 day23kit라는 도구 상자에서 DB 연결, AI 번역기(인코더), 연습용 검색 도구를 미리 가져옵니다.
from time import perf_counter
from day23kit.fixtures import fixture_search
from day23kit.embedding import get_encoder, encode_question
from day23kit.db import connect_db, exact_topk, check_data_ready
from day23kit.io import save_result


# 전체적인 접근 방식 (큰 그림)

# 검색 프로그램이 똑똑하게 작동하려면 3단계를 거쳐야 합니다.
# 1. 질문 검사 (validate_question): "질문을 제대로 적었니? 빈칸만 보낸 건 아니지?" 하고 확인합니다.
# 2. 자료 찾기 (retrieve_candidates): 연습 모드(fixture)면 미리 준비된 모의고사 답안지를 꺼내고, 실전 모드(live)면 질문을 AI 숫자(벡터)로 바꾼 뒤 진짜 도서관(DB)에서 가장 비슷한 자료를 찾아옵니다.
# 3. 결과 예쁘게 포장하기 (format_candidates): 찾아온 자료에서 필요한 정보만 쏙쏙 뽑아 깔끔한 명함 모양으로 정리합니다.
# 4. main() (접수 창구): 사용자가 터미널에 입력한 명령어 옵션(--mode, --question, --k 등)을 받아서, 총지휘자인 run()에게 전달하고 최종 결과표를 영수증(exercise_08.json)으로 출력합니다.
# 5. run() (총지휘자): 난이도(level)에 맞춰 검색 조건을 세팅하고, 시간을 재면서 자료를 찾은 뒤, 다음 단계(LLM 답변 생성)로 넘길 수 있도록 최종 보고서(result)를 포장합니다.

# 1단계: 질문이 제대로 된 글자인지 검사하기(validate_question)
# BEGIN D23-08-B01
def validate_question(question):
    """
    TODO D23-08-B01 · validate_question
        질문은 1자 이상의 문자열이어야 하며 앞뒤 공백을 제거하세요.
        빈 값/공백만 있는 값이면 ValueError. 반환은 정리된 질문.
        API가 연결되어 있지 않아도 검사 가능한 순수 함수입니다.
    """ # 
    if not isinstance(question, str)or not question.strip():raise ValueError('empty_question') # isinstance(question, str) 명령어로 질문이 글자(문자열)가 맞는지 판단하고 숫자나 빈 값이면 탈락 처리합니다.
                                                                                               # not question.strip() 명령어로 앞뒤 빈칸(스페이스바)을 다 지웠을 때 아무 글자도 안 남았는지 확인합니다.
                                                                                               # raise ValueError(...) 명령어로 빈칸만 확인되면 "빈 질문입니다"라고 경고(에러)를 띄워 멈춥니다.
    return question.strip() # 정상적인 질문이라면 앞뒤의 불필요한 공백만 깔끔하게 잘라서 돌려줍니다.
# END D23-08-B01

# 2단계: 연습 모드 vs 실전 DB에서 자료 찾기 (retrieve_candidates)
# BEGIN D23-08-B02
def retrieve_candidates(question,mode,k,category,env_file):
    """
    TODO D23-08-B02 · retrieve_candidates
        fixture면 교육용 fixture_search, live면 E5 query Embedding → pgvector Exact SQL을 사용하세요.
        실제 live는 exercise05에서 9개 자료를 먼저 저장해야 합니다.
        DB 연결 실패를 빈 결과 []로 바꾸지 말고 예외를 전달하세요.
    """ # 
    if mode == 'fixture': # 연습 모드로 실제 DB를 켜지 않고, 미리 만들어 둔 fixture_search(연습용 데이터)에서 관련 자료 k개를 바로 꺼내옵니다.
        return fixture_search(question, k, category)
    encoder = get_encoder('live')
    qvec = encode_question(encoder, question) # 실전 모드로 question(사람의 글자)을 qvec(벡터, AI가 이해할 수 있는 숫자 좌표)로 변환합니다.(비슷한 뜻의 문장은 비슷한 숫자 좌표를 가집니다.)
    with connect_db(env_file) as conn: # 비밀번호가 적힌 .env 파일을 이용해 실제 PostgreSQL 데이터베이스에 접속합니다. (with를 쓰면 볼일이 끝난 뒤 문을 자동으로 안전하게 닫아줍니다.)
        check_data_ready(conn) # DB 안에 데이터가 제대로 있는지 먼저 확인합니다.
        return exact_topk(conn, qvec, k, category) # qvec(질문 좌표)와 거리가 가장 가까운 자료 k개를 정확하게 찾아옵니다.
# END D23-08-B02

# 3단계: 찾아온 결과 예쁘게 정리하기 (format_candidates)
# BEGIN D23-08-B03
def format_candidates(hits): # DB에서 hits(찾아온 검색 결과 목록)를 하나씩 꺼내서(for h in hits) 똑같은 모양의 딕셔너리(정보 카드)로 다시 포장합니다.
    """
    TODO D23-08-B03 · format_candidates
        후보의 id/title/content/category/source_version/distance를 반환하세요.
        검색된 원문을 요약·변조하지 않고, distance는 숫자 그대로 둡니다.
        답변 상태(answered)를 자동으로 부여하지 마세요.
    """ # 
    return [{'id': h['id'], 'title': h['title'], 'content': h['content'], 'category': h['category'], 'source_version': h['source_version'], 'distance': round(float(h['distance']), 6)} for h in hits] # distance(질문과 자료 사이의 거리)는 소수점이 아주 길게 나오기 때문에, 소수점 아래 6자리까지만 반올림해서 깔끔하게 만듭니다.(거리가 0에 가까울수록 질문과 뜻이 똑같다는 의미입니다)
# END D23-08-B03


# 총지휘자 함수: run(mode, level, args)
def run(mode,level,args): # args에서 사용자가 입력한 질문(question)을 꺼내 검사합니다.
    question=validate_question(getattr(args,'question','서버는 어디에서 실행하나요?')) # 만약 질문이 없으면 기본값인 '서버는 어디에서 실행하나요?'를 사용합니다.
    k=3 if level==1 else args.k # level == 1(기초 단계)일 때는 사용자가 다른 값을 넣었더라도 무조건 검색 개수 k = 3, 카테고리 필터 None(전체 검색)으로 고정합니다.
    category=None if level==1 else args.category
    if level>=2:options=validate_options(k,category) # level >= 2(심화 단계)부터는 사용자가 직접 지정한 args.k와 args.category 값을 검사(validate_options)해서 사용합니다.
    else:options={'k':k,'category':category}
    t0=perf_counter() # perf_counter() 함수(초시계 측정)로 자료를 찾기 직전 시간(t0)을 기록하고, 검색이 끝나자마자 걸린 시간을 계산해 밀리초(ms, 1000분의 1초) 단위로 바꿉니다.(검색 속도가 얼마나 빠른지 재는 스톱워치 역할입니다.)
    hits=retrieve_candidates(question,mode,options['k'],options['category'],Path(__file__).with_name('.env')) # 현재 파일과 같은 폴더에 있는 .env 비밀 설정 파일을 넘겨주며 hits(자료)를 찾고, formatted(깔끔한 카드 모양)로 정리합니다.
    elapsed=(perf_counter()-t0)*1000
    formatted=format_candidates(hits)
    result=dict(exercise=8,level=level,source_mode='simulated' if mode=='fixture' else 'pgvector_exact',question=question,options=options,
                retrieved=formatted,retrieved_count=len(formatted),human_evidence_ok=None,
                next_step='검토 후 Context 후보로 전달; LLM 답변 생성은 Day25 RAG에서 수행') # fixture(연습 모드)였는지 pgvector_exact(실전 DB 모드)였는지 표시하고, 찾아낸 자료 목록(retrieved)과 개수(retrieved_count)를 한 상자에 담습니다.
    if level>=2:result['run_report']=make_run_report(question,hits,mode,elapsed) # 나중에 level이 2나 3으로 올라가면 실행 보고서(run_report)나 모델 버전 검사(contract_check) 항목도 자동으로 추가되도록 설계되어 있습니다.(현재는 level=1이므로 기본 항목만 담깁니다.)
    if level>=3:result['contract_check']=check_model_and_versions(hits,mode)
    return result


# 접수 창구 및 실행기: main()
def main():
    parser=argparse.ArgumentParser(description='Day23 실습 08 · AI Agent용 Retriever') # 우리가 터미널에 python main.py --mode live --question "안녕"처럼 입력한 글자들을 파이썬이 이해할 수 있도록 옵션별로 분류해 args에 담아줍니다.(명령어 통역기)
                                                                                      # 아무것도 안 적으면 default로 정해진 기본값이 들어갑니다.
    parser.add_argument('--mode',choices=['fixture','live'],default='fixture',
        help='fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계')

    parser.add_argument('--question',default='서버는 어디에서 실행하나요?',help='검색 질문')
    parser.add_argument('--k',type=int,default=3,help='반환할 최대 검색 후보 (1~9)')
    parser.add_argument('--category',default=None,choices=['course','development','support'],help='Metadata 분류 필터')
    args=parser.parse_args()
    result=run(args.mode,1,args) # level을 1로 고정해서 run()을 실행하고, 그 결과를 현재 폴더에 exercise_08.json 파일로 저장합니다.
    path=save_result(Path(__file__).resolve().parent,'exercise_08.json',result)
    import json
    print(json.dumps(result,ensure_ascii=False,indent=2,default=str)) # ensure_ascii=False 명령어로 한글이 \uXXXX처럼 외계어로 깨지지 않고 원래 한글 그대로 보이게 합니다.
                                                                      # indent=2 명령어로 한 줄로 길게 출력되지 않고 2칸씩 들여쓰기 해서 사람이 읽기 편하게 보여줍니다.
    print('결과 저장:',path)

if __name__=='__main__': # 다른 파일에서 이 코드를 부품으로 불러올 때 말고, 이 파일을 직접 실행했을 때만 main() 함수를 시작하는 파이썬의 표준 약속입니다.
    main()

"""
20261118_01
output.json 검토 결과
...
...
...
"""