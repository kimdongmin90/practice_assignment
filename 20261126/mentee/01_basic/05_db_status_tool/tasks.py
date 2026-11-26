"""05 · PostgreSQL Read-only lookup_status · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def parse_report_id(value) -> int:
    """task_id가 아니라 reports.report_id. 임의로 문자열을 SQL에 붙이지 않습니다."""
    from coursekit.contracts import report_id_from
    return report_id_from(value)
    # TODO D29-05-B-01: task_id가 아니라 reports.report_id. 임의로 문자열을 SQL에 붙이지 않습니다.
    # 힌트: index_status는 DB 인덱싱 상태이며 vector_fresh는 별도 검사 값입니다.

def status_view(raw: dict) -> dict:
    """pending/ready/failed와 실제 벡터 정합성을 구분해 표시."""
    if raw['status']!='ok':return {'status':'not_found','report_id':raw['report_id']}
    return {'report_id':raw['report_id'],'index_status':raw['index_status'],
            'revision':raw['revision'],'vector_fresh':raw['vector_fresh']}
    # TODO D29-05-B-02: pending/ready/failed와 실제 벡터 정합성을 구분해 표시.
    # 힌트: index_status는 DB 인덱싱 상태이며 vector_fresh는 별도 검사 값입니다.
