"""실습 03 Basic · 일반 prose 전용 cleaning."""

# 1. 엔터(줄바꿈) 통일하기 (unify_newlines): 윈도우식 엔터(\r\n)와 옛날 맥식 엔터(\r)를 모두 표준 엔터(\n) 하나로 통일합니다.
# 2. 띄어쓰기 정리하기 (reduce_horizontal_spaces): 스페이스바를 2~3번씩 잘못 누른 빈칸들을 딱 1칸으로 줄이고, 문장 앞뒤의 쓸데없는 공백을 잘라냅니다.(단, 문단을 나누는 빈 줄 \n\n은 망가지지 않게 그대로 살려둡니다)

# 준비물 챙기기 (도구 불러오기)
from pathlib import Path
import re,sys # 글자 속에서 특정 패턴(예: "빈칸이 여러 개 붙어 있는 곳")을 찾아 바꿔주는 정규표현식 도구 re를 가져옵니다.
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
from coursekit.io import DATA, save_json, show_success # cleaning.json(결과를 파일)로 저장해 주는 도구 상자입니다.


# 1단계 청소: 엔터(줄바꿈) 모양 통일하기 (unify_newlines)
def unify_newlines(text:str)->str: # 컴퓨터 운영체제마다 줄을 바꿀 때 숨겨진 기호를 다르게 씁니다.(윈도우는 \r\n, 옛날 맥은 \r, 리눅스/파이썬 표준은 \n)
    # BEGIN D24-03-B01
    # TODO D24-03-B01 : CRLF·CR 줄바꿈을 LF로 바꿉니다. 문단의 줄을 하나로 합치지 않습니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # CRLF와 CR을 차례로 LF로 바꾸도록 any 두 곳을 채우세요.
    return text.replace('\r\n','\n').replace('\r','\n') # 먼저 2글자짜리 \r\n을 \n으로 바꾼 뒤, 남은 \r을 \n으로 바꿉니다. 만약 \r부터 바꾸면 \r\n이 \n\n으로 변해서 줄바꿈이 두 번 일어나는 사고가 납니다.(순서가 중요)
    # END D24-03-B01

#  2단계 청소: 가로 띄어쓰기 깔끔하게 줄이기 (reduce_horizontal_spaces)
def reduce_horizontal_spaces(text:str)->str:
    """줄 단위 변환이므로 빈 줄이 사라지지 않습니다."""
    # BEGIN D24-03-B02
    # TODO D24-03-B02 : 연속된 공백·탭을 한 칸으로 줄이고 좌우 공백을 제거합니다. 빈 줄은 보존합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # 줄 단위로 처리할 목록을 any 대신 작성하세요. 빈 줄은 보존해야 합니다.
    return '\n'.join(re.sub(r'[ \t]+',' ',line).strip()
                     for line in text.split('\n')).strip() # text.split('\n') 명령어로 전체 글을 엔터(\n) 기준으로 한 줄씩 잘라서 리스트로 만듭니다.(이렇게 한 줄씩 떼어내야 문단을 나누는 엔터 \n\n이 지워지지 않고 안전하게 보호됩니다.)
                                                           # re.sub(r'[ \t]+', ' ', line) 명령어로 각 줄(line)에서 스페이스바( )나 탭(\t)이 1개 이상 연속으로 붙어 있는 곳([ \t]+)을 찾아 스페이스바 딱 1칸(' ')으로 바꿉니다.
                                                           # .strip() 함수로 각 줄의 맨 앞과 맨 뒤에 붙어 있는 불필요한 공백을 싹 잘라냅니다.
                                                           # '\n'.join(...) 명령어로 깔끔하게 청소가 끝난 줄들을 다시 엔터(\n)로 이어 붙여 원래의 문단 모양으로 조립합니다.
    # END D24-03-B02

# 실행 및 검사하기 (main)
def main():
    text='출석   안내\r\n\r\n10분  초과는 결석.\r\n단,  사전 승인 시 예외.' # 띄어쓰기가 2~3칸씩 들어가 있고(\r\n도 섞여 있는) 지저분한 원본 문장입니다.
    cleaned=reduce_horizontal_spaces(unify_newlines(text)) # unify_newlines로 엔터를 먼저 통일한 뒤, 그 결과를 reduce_horizontal_spaces에 넣어 띄어쓰기를 정리합니다.
                                                           # '출석 안내\n\n10분 초과는 결석.\n단, 사전 승인 시 예외.'(cleaned 후 결과)
    assert '10분 초과는 결석.' in cleaned # 두 칸 띄어쓰기였던 '10분  초과는'이 '10분 초과는'으로 잘 고쳐졌는지, 그리고 문단 구분용 빈 줄('\n\n')이 안 지워지고 잘 살아있는지 스스로 검사합니다.
    assert '\n\n' in cleaned
    out=save_json(HERE,'cleaning.json',{'before':repr(text),'after':cleaned}) # 결과 파일(cleaning.json)에 저장할 때, 눈에 안 보이는 \r\n 기호까지 글자 그대로 보여주기 위해 repr()을 사용합니다.
    show_success('03 Basic',out)

if __name__=='__main__':main()
