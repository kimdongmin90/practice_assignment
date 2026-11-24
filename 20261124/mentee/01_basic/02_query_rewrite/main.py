"""Day27 강의 실습. 실행은 역할 폴더에서 Python으로 실행합니다."""
# 전체적인 접근 방식 (큰 그림)
# 이 코드는 직접 모든 기능을 밑바닥부터 짜지 않고, 미리 만들어둔 도구 상자(coursekit)에서 필요한 부품만 꺼내 조립하는 방식을 씁니다.
# 1. 작업 준비: 내 컴퓨터 어디에 도구가 있는지 위치를 찾습니다.
# 2. 도구(함수) 만들기: 질문을 고치는 기계와, 고친 결과를 메모지에 적는 기계를 만듭니다.
# 3. 실행 및 저장: 미리 짜인 채점기(STAGE_RUNNERS)에 위 두 기계를 넣어서 돌린 뒤, 결과 파일을 저장합니다.
# ① 도구 위치를 찾고 → ② '질문 고치기'와 '결과 적기' 규칙을 만든 뒤 → ③ 실행 모드(연습/실전)에 맞춰 자동으로 테스트를 돌리고 결과 파일을 저장하는 자동화 스크립트

# 준비 단계: 도구 상자 위치 찾기
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent # 지금 실행 중인 이 파이썬 파일이 들어있는 현재 폴더를 뜻합니다.
ROLE_ROOT=next(p for p in HERE.parents if (p/'coursekit').is_dir()) # 현재 폴더에서 위로 한 칸씩 올라가면서 coursekit(수업용 도구 상자) 폴더가 어디 있는지 찾아냅니다.
sys.path.insert(0,str(ROLE_ROOT)) # 파이썬에게 *"이 도구 상자 폴더 안의 파일들을 자유롭게 꺼내 쓸 수 있게 등록해 줘"*라고 알려주는 코드입니다.


import argparse
from coursekit.workshops import STAGE_RUNNERS
from coursekit.io import save_report


# 핵심 기능 만들기: 질문 고치기 & 기록하기
def apply_rewrite(question, history, offline):
    """offline이면 고정 예시, 기본 실행이면 실제 ChatPromptTemplate → Chat Model을 호출합니다."""
    from coursekit.rewrite import rewrite_query
    return rewrite_query(question, history, offline) # question(현재 질문), history(이전 대화 내역), offline(인터넷 연결 여부)을 받아서, 도구 상자에 있는 rewrite_query라는 전문가에게 넘깁니다.
    # BEGIN D27-02-B01
    # TODO D27-02-B01: offline이면 고정 예시, 기본 실행이면 실제 ChatPromptTemplate → Chat Model을 호출합니다.
    # END D27-02-B01


def record_rewrite(original, result): # 시험을 치고 나면 오답 노트를 쓰듯, 결과를 깔끔한 표(딕셔너리) 형태로 정리합니다.
    """원래 질문을 검색 질문으로 덮어쓰지 않습니다."""
    return {'original_question': original, 'search_query': result.search_query, 'status': result.status, 'reason': result.reason} # 원래 질문(original_question), 바뀐 검색어(search_query), 성공 여부(status), 그렇게 바꾼 이유(reason) 4가지를 짝지어서 기록합니다.
    # BEGIN D27-02-B02
    # TODO D27-02-B02: 원래 질문을 검색 질문으로 덮어쓰지 않습니다.
    # END D27-02-B02


# 실행 단계: 옵션 확인하고 채점기 돌리기
def main():
    parser=argparse.ArgumentParser(description='Day27 실습 02 · 02_query_rewrite') # 터미널에서 프로그램을 실행할 때 옵션을 붙일 수 있게 해줍니다.
    parser.add_argument('--offline',action='store_true',help='교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.') # • 사용자가 실행할 때 --offline을 붙이면 True(참)가 됩니다.
                                                                                                            # 인터넷이나 실제 AI 모델 대신 미리 정해진 연습용 데이터로 빠르게 테스트하겠다는 뜻입니다.
    args=parser.parse_args()
    # Day27: 일부 진단 실습 외에는 기본 실행이 실제 모델·DB·LLM 경로입니다.
    report=STAGE_RUNNERS[2](args.offline,[apply_rewrite,record_rewrite]) # 미리 만들어진 2단계 실습 진행자(STAGE_RUNNERS[2])에게 오프라인 여부와, 우리가 위에서 만든 두 함수([apply_rewrite, record_rewrite])를 전달합니다.
                                                                         # • 진행자가 알아서 문제들을 하나씩 꺼내 apply_rewrite로 풀고, record_rewrite로 채점 결과를 모아서 report(최종 성적표)를 만듭니다.
    # 마무리 단계: 결과 파일로 저장하기
    path=save_report(HERE,'day27_02_'+('fixture' if args.offline else 'live')+'.json',report) # 완성된 성적표(report)를 현재 폴더(HERE)에 .json 파일로 저장합니다.
                                                                                              # 오프라인 모드였다면 파일 이름에 fixture(연습용)가 붙고, 실제 모델을 썼다면 live(실전용)가 붙습니다.
    print('실습 02 결과:', path)
    print('보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.')

if __name__=='__main__':main() # 이 파일을 다른 곳에서 부품으로 불러온 게 아니라, 직접 실행했을 때만 main() 함수를 시작하라는 파이썬의 기본 약속입니다.