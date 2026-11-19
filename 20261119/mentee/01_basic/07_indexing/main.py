"""실습 07 Basic · 기본 실행은 데이터 계약, --live-db는 실제 E5/DB 실행."""

# 1. 문서 준비 및 품질 검사 (select_index_chunk): 책을 자른 조각(청크)이 빈 종이는 아닌지, AI 모델(E5)이 좋아하는 약속된 이름표('passage: ')가 맨 앞에 잘 붙어 있는지 꼼꼼히 검사합니다.
# 2. 검색 결과 표준화 (format_hit): DB에서 찾아온 검색 결과에 출처 번호(citation_id)가 제대로 붙어 있는지 확인하고, 보기 좋은 명함 모양(딕셔너리)으로 정리합니다.
# 3. 안전한 2단계 모드 실행 (main):
# 	기본 모드 (연습): DB가 꺼져 있어도 코드가 잘 돌아가는지 준비물만 포장해서 indexing.json에 저장합니다.
# 	실전 모드 (--live-db): 터미널에 옵션을 주면 실제로 AI 모델을 켜서 글을 숫자로 바꾸고, DB에 임시 등록(stage) 후 정식 공개(publish)까지 한 뒤 테스트 검색을 실행합니다.

from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
from coursekit.io import save_json, show_success
from coursekit.documents import by_doc,parse_one
from coursekit.processing import make_chunks


# select_index_chunk(doc_id: str) — 인덱싱할 문서 조각 고르고 검사하기
def select_index_chunk(doc_id:str)->tuple[dict,dict]:
    # BEGIN D24-07-B01
    # TODO D24-07-B01 : 기존 DOC-ASSIGN 텍스트에서 유효한 청크 1건을 선택하고 E5 passage 입력을 확인합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    doc=by_doc(doc_id) # 'DOC-ASSIGN'(문서 번호)로 원본 문서를 찾아 글자로 해독합니다.
    parsed=parse_one(doc) # 해독 상태가 'parsed'가 아니면 "등록할 수 없는 문서"라며 멈춥니다.
    if parsed['status']!='parsed':
        raise ValueError('not indexable')
    chunks=make_chunks(doc,parsed['units'][0],size=110,overlap=15) # make_chunks(..., size=110, overlap=15) 명령어로 긴 글을 110글자씩 자르되, 문맥이 끊기지 않도록 overlap(앞뒤 조각이 15글자씩 겹치게)하여 자릅니다.
    # 첫 번째 유효 Chunk의 인덱스와 E5 접두어를 any 대신 작성하세요.
    first=chunks[0]
    if not first['body'].strip() or not first['embedding_text'].startswith('passage: '):
        raise ValueError('bad embedding input') # first(첫 번째 조각)의 body(본문)가 비어 있으면 안 됩니다.
                                                # E5 임베딩 모델은 저장할 문서 앞에 반드시 'passage: '이라는 꼬리표를 붙여야 성능이 잘 나오기 때문에, .startswith('passage: ')로 꼬리표가 잘 붙었는지 확인합니다.
    return doc,first
    # END D24-07-B01

# format_hit(row: tuple) — 검색 결과를 깔끔한 출처 카드로 바꾸기
def format_hit(row:tuple)->dict:
    """DB 행: citation_id,chunk_id,body,locator,doc_id,version,distance."""
    # BEGIN D24-07-B02
    # TODO D24-07-B02 : DB 검색 결과 행을 정수 citation_id·chunk_id·본문·출처·거리의 딕셔너리로 변환합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    cid,chunk_id,body,locator,doc_id,source_version,distance=row # DB에서 7개 정보가 한 줄로 묶여 온 row를 cid, chunk_id, body 등 7개 변수에 각각 나눕니다.
    if type(cid) is not int or cid<=0: # type(cid) is not int or cid <= 0 명령어로 나중에 AI 답변에 [출처 1]처럼 번호를 달아주기 위해, citation_id가 반드시 1 이상의 정수인지 검사합니다.(파이썬에서 True는 숫자 1과 같게 취급되므로 isinstance 대신 type(cid) is not int로 더 엄격하게 검사합니다.)
        raise ValueError('invalid citation ID')
    # any 두 곳을 반환값과 거리 입력 변수로 바꾸세요.
    return {'citation_id':cid,'chunk_id':chunk_id,'body':body,
            'source_locator':locator,'doc_id':doc_id,
            'source_version':source_version,'cosine_distance':float(distance)}
    # END D24-07-B02

# main() — 연습 모드 & 실전 DB 모드 지휘하기
def main():
    doc,chunk=select_index_chunk('DOC-ASSIGN')
    output={'source_mode':'prepared_only_not_db','chunk':chunk,
            'live_db':'not_run','sample_hit_contract':format_hit((201,chunk['chunk_id'],chunk['body'],chunk['source_locator'],doc['doc_id'],'v1',0.0))} # 기본 실행(연습 모드)으로 DB에 연결하지 않고도 format_hit이 잘 작동하는지 가짜 번호(201)를 넣어 샘플 계약을 확인하고, live_db는 'not_run'(미실행)으로 기록합니다.
    if '--live-db' in sys.argv: # if '--live-db' in sys.argv 명령어로 사용자가 터미널에서 실행할 때 --live-db라는 옵션을 적었는지 확인합니다.
        from coursekit.live import connect_db,load_encoder,encode_passages,encode_query
        from coursekit.db import initialize,stage_version,publish_version,search_current,use_schema
        # 실제 모델 추론은 DB 트랜잭션 전에 수행합니다.
        model=load_encoder();vectors=encode_passages(model,[chunk]) # encode_passages() 명령어로 model(AI 번역기)를 불러와 문서 조각은 vectors로
        query=encode_query(model,'과제 파일은 어디에 보관하나요?') # encode_query() 함수로 질문('과제 파일은 어디에 보관하나요?')은 query 숫자로 바꿉니다.
        with connect_db() as conn: # with conn.transaction() 명령어로 작업 도중 에러가 나면 없던 일로 되돌려주는 안전장치를 설정합니다.(트랜잭션(Transaction) 처리)
            use_schema(conn,'d24_basic07')
            initialize(conn)
            with conn.transaction():
                stage_version(conn,doc,doc['file'],[chunk],vectors) # 새 버전 문서를 stage(임시 창고)에 먼저 올립니다. 
                publish_version(conn,doc['doc_id'],doc['source_version'],chunk['pipeline_version']) # 문제가 없을 때 publish(실제 검색 대상)로 전환하는 현업의 무중단 배포 방식입니다.
            result=search_current(conn,query,category='학사',k=3) # search_current(...) 명령어로 방금 등록한 DB에서 '학사' 카테고리 중 내 질문과 가장 비슷한 자료 3개(k=3)를 찾아옵니다.
            output['source_mode']='e5_pgvector_live'
            output['live_db']=[format_hit(r) for r in result]
    out=save_json(HERE,'indexing.json',output)
    show_success('07 Basic',out)

if __name__=='__main__':main()
