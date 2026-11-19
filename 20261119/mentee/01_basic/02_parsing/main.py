"""실습 02 Basic · TXT parsing의 기본."""
# 준비물 챙기기 (경로 설정 및 도구 불러오기)
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent # HERE.parents에 있는 coursekit.io 도구 상자에서 원본 데이터 폴더 위치(DATA)와 결과 저장 기능(save_json)을 가져옵니다.
sys.path.insert(0,str(HERE.parents[1]))
from coursekit.io import DATA, save_json, show_success

# 1. 암호 해독 (decode_text): 바이트(bytes) 데이터를 한글과 영어가 보이는 글자(str)로 번역합니다.
# 2. 빈 파일 검사 (if not text.strip()): 번역해 봤더니 속이 텅 빈 백지 파일이라면 다음 단계로 넘어가지 못하게 막습니다.
# 3. 출처 이름표 붙이기 (make_unit): 나중에 AI가 이 내용을 보고 대답할 때 "이 정보는 어느 문서의 몇 페이지에서 나왔어요!"라고 정확히 알려줄 수 있도록 출처 기록 카드를 만듭니다.


# 바이트를 글자로 번역하기: decode_text(raw: bytes) -> str
def decode_text(raw:bytes)->str:
    """errors='ignore'를 쓰면 누락을 탐지하기 어렵습니다."""
    # BEGIN D24-02-B01
    # TODO D24-02-B01 : 원문 바이트를 UTF-8로 디코딩해 str을 반환합니다. 잘못된 입력은 무시하지 않습니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # any를 UTF-8 디코딩에 사용할 Encoding 이름으로 교체하세요.
    return raw.decode('utf-8-sig') # 파일에서 막 읽어온 raw는 사람 눈에는 보이지 않는 바이트 숫자 덩어리입니다.
                                   # .decode('utf-8-sig')를 쓰면 이를 우리가 읽을 수 있는 글자(str)로 바꿔줍니다.
                                   # 윈도우 메모장 등에서 UTF-8로 저장하면 파일 맨 앞에 눈에 안 보이는 투명한 표시(BOM)가 붙는 경우가 종종 있습니다.
                                   # utf-8-sig를 사용하면 글자를 번역하면서 그 투명 표시까지 깔끔하게 지워줍니다.

    # END D24-02-B01

# 출처 이름표(단위 객체) 만들기: make_unit(...) -> dict
def make_unit(doc_id:str,source_version:str,text:str)->dict:
    """TXT에는 페이지 번호가 없으므로 None. 가짜 page 1을 만들지 않습니다."""
    # BEGIN D24-02-B02
    # TODO D24-02-B02 : 추출된 문자열을 doc_id·버전·unit_id·source_locator와 함께 한 건의 ParsedUnit으로 묶습니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    return {'doc_id': doc_id,'source_version': source_version,
            'unit_id':'text-1','source_locator':'assignment.txt',
            'page_number':None,'raw_text':text} # 'DOC-ASSIGN'(문서 고유 번호)
                                                # 문서 버전('v1', 나중에 내용이 수정되면 'v2'로 구분하기 위함)
                                                # 'text-1'(이 문서 안에서 몇 번째 조각인지 나타내는 번호)
                                                # 'assignment.txt'(원본 파일 이름)
                                                # PDF 책이라면 몇 페이지인지 적는 칸인데, 일반 텍스트(.txt) 파일은 페이지 개념이 없으므로 None(없음)으로 표시합니다.
                                                # 방금 번역한 실제 글자 내용 전체(raw_text)입니다.
    # END D24-02-B02

# 실행 및 저장하기: main()    
def main():
    raw=(DATA/'raw'/'assignment.txt').read_bytes() # 파일을 바이트로 읽어(read_bytes) 글자로 바꿉니다(decode_text).
    text=decode_text(raw)
    if not text.strip():raise ValueError('empty text') # 앞뒤 빈칸이나 엔터를 다 지웠을 때 글자가 한 글자도 없다면(empty text), 빈 문서를 처리하는 헛수고를 막기 위해 에러를 내고 멈춥니다.
    unit=make_unit('DOC-ASSIGN','v1',text)
    out=save_json(HERE,'parsed_unit.json',unit)
    show_success('02 Basic',out) # 모든 검사를 통과하면 make_unit으로 만든 출처 카드를 현재 폴더(HERE)에 parsed_unit.json 파일로 저장하고 성공 메시지를 띄웁니다.

if __name__=='__main__':main()
