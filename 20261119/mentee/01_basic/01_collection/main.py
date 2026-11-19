"""실습 01 Basic · Python 파일 하나로 원문을 수집합니다."""

# 바이트 단위 원본 보존 (read_bytes): 수집 단계에서는 인코딩 변환(UTF-8 등)이나 파싱을 먼저 시도하지 않고, 원본 파일의 바이트(bytes) 그대로를 읽어 데이터 변형을 원천 차단합니다.
# 데이터 무결성 및 중복 방지 (sha_bytes): 파일 내용 전체를 SHA-256 해시값(raw_sha256)으로 변환해 기록함으로써, 추후 문서가 수정되었는지 또는 동일한 문서가 중복 수집되었는지 즉시 판별할 수 있게 합니다.
# 단일 책임 분리: 파일 읽기(read_raw), 메타데이터 구조화(build_record), 실행 및 저장(main)을 명확히 분리해 테스트와 재사용이 쉽도록 구성했습니다.

# 경로 설정 및 유틸리티 임포트
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent # HERE(현재 스크립트 위치)에서 두 단계 상위 폴더(HERE.parents)를 파이썬 모듈 검색 경로에 추가하여, coursekit 패키지의 데이터 경로(DATA), JSON 저장(save_json), 바이트 해싱(sha_bytes) 도구를 불러옵니다.
sys.path.insert(0,str(HERE.parents[1]))
from coursekit.io import DATA, save_json, show_success
from coursekit.documents import sha_bytes


# 원본 바이트 읽기: read_raw(path: Path) -> bytes
def read_raw(path:Path)->bytes: # path(전달받은 경로)• 에 실제 파일이 존재하는지 먼저 확인한 뒤, 파일의 바이너리 원본 데이터를 bytes 객체로 읽어 반환합니다.
    """입력: Path / 출력: bytes. 원본 파일은 수정하지 않습니다."""
    # BEGIN D24-01-B01
    # TODO D24-01-B01 : 입력 경로의 파일을 bytes로 읽어 반환합니다. 없는 파일은 명확히 실패해야 합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다. 
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_bytes()
    # END D24-01-B01


# 수집 레코드(메타데이터) 생성: build_record(...) -> dict
def build_record(doc_id:str,path:Path,raw:bytes)->dict: # 수집된 원본 파일의 핵심 정보를 표준화된 딕셔너리 형태로 조립합니다.
    """파일명은 식별자가 아닙니다. 문서 ID와 원본 바이트 해시를 별도로 보관합니다."""
    # BEGIN D24-01-B02
    # TODO D24-01-B02 : 문서 ID·원문 파일명·바이트 수·SHA-256을 한 딕셔너리에 묶습니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # any는 수강생이 알맞은 변수·표현식으로 교체할 자리 표시자입니다.
    return {'doc_id': doc_id,'filename': path.name,'size_bytes':len(raw), # doc_id 명령어로 문서를 식별하기 위한 고유 ID('DOC-ASSIGN')를 확인합니다.
                                                                          # filename 명령어로 경로를 제외한 순수 파일명('assignment.txt')을 확인합니다.
                                                                          # size_bytes 명령어로 바이트 배열의 길이(len(raw))를 통한 정확한 파일 크기를 확인합니다.
                                                                          # raw_sha256 명령어로 원본 바이트의 SHA-256 해시 지문을 확인합니다.
                'raw_sha256':sha_bytes(raw)}
    # END D24-01-B02


# 실행 및 결과 저장: main()
def main():
    path=DATA/'raw'/'assignment.txt' # DATA/raw/assignment.txt 파일을 읽어 'DOC-ASSIGN'이라는 ID로 레코드를 생성합니다.
    raw=read_raw(path)
    record=build_record('DOC-ASSIGN',path,raw)
    assert record['size_bytes']==len(raw) # assert 문으로 기록된 바이트 크기와 실제 읽은 바이트 길이가 일치하는지 검증한 뒤, 현재 폴더(HERE)에 collection.json 파일로 저장하고 성공 메시지를 출력합니다.
    out=save_json(HERE,'collection.json',record)
    show_success('01 Basic',out)

if __name__=='__main__':main()
