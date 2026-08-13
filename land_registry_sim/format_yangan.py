"""
format_yangan.py

'양안식' 기록 방식: 필지 정보를 순수 문자열(줄글 서술)로만 저장한다.
조선 양안이 자호·지번·등급·사표 등을 모두 문장 형태로 기록했다는 점을
재현한 것으로, 컴퓨터가 이해할 수 있는 구조(표, 필드)가 전혀 없다는 게
핵심 특징이다.

검색/집계를 하려면 문자열을 파싱하거나 정규식을 써야 하며,
이는 데프테리식(표)에 비해 코드가 길어지고 느려진다는 걸 보여주기 위한
비교 대상(baseline) 역할을 한다.
"""

import re
from typing import List
from data_generator import Parcel, tax_of


def to_yangan_text(parcel: Parcel) -> str:
    """필지 하나를 양안식 문장으로 변환한다."""
    neighbor_str = ", ".join(f"{n}번" for n in parcel.neighbors) if parcel.neighbors else "없음"
    return (
        f"자호 {parcel.id}번. 소유주는 {parcel.owner}이다. "
        f"토지 등급은 {parcel.grade}등이며, 결부수는 {parcel.area}이다. "
        f"사표(인접 필지)는 {neighbor_str}이다."
    )


def build_yangan_record(parcels: List[Parcel]) -> List[str]:
    """마을 전체를 양안식 문장 리스트로 변환한다. (== 양안 한 책)"""
    return [to_yangan_text(p) for p in parcels]


# ---------------------------------------------------------------------
# 아래는 "텍스트만으로" 질의를 처리하는 함수들.
# 표 구조가 없으므로 전수 스캔 + 문자열/정규식 매칭이 유일한 방법이다.
# ---------------------------------------------------------------------

def find_by_owner_text(record: List[str], owner_name: str) -> List[str]:
    """소유주 이름으로 필지 문장을 찾는다. (전수 스캔 + 부분 문자열 매칭)"""
    return [line for line in record if f"소유주는 {owner_name}" in line]


def sum_tax_by_grade_text(record: List[str], grade: str) -> int:
    """
    등급별 세액 합계를 구한다.
    표가 없으므로 각 문장에서 등급과 결부수를 정규식으로 다시 추출해야 한다.
    이 재추출 과정 자체가 비구조화 텍스트의 비용을 보여주는 부분이다.
    """
    pattern = re.compile(r"토지 등급은 (\S)등이며, 결부수는 (\d+)이다")
    tax_rate = {"상": 3, "중": 2, "하": 1}
    total = 0
    for line in record:
        m = pattern.search(line)
        if not m:
            continue
        g, area = m.group(1), int(m.group(2))
        if g == grade:
            total += area * tax_rate[g]
    return total


def find_adjacent_parcels_text(record: List[str], parcel_id: int) -> List[int]:
    """
    특정 필지와 인접한 필지 id 목록을 구한다.
    텍스트 안에서 '사표' 문장을 정규식으로 파싱해야 하며,
    공간적 위치 관계(어느 쪽이 동/서/남/북인지)는 애초에 텍스트에
    구조화되어 있지 않으므로 별도 좌표 없이는 알 수 없다는 한계가 있다.
    """
    target_prefix = f"자호 {parcel_id}번."
    for line in record:
        if line.startswith(target_prefix):
            m = re.search(r"사표\(인접 필지\)는 (.+?)이다\.", line)
            if not m or m.group(1) == "없음":
                return []
            ids_str = m.group(1)
            return [int(x.replace("번", "")) for x in ids_str.split(", ")]
    return []


if __name__ == "__main__":
    from data_generator import generate_village

    village = generate_village()
    record = build_yangan_record(village)

    print("=== 양안식 기록 예시 (앞 3건) ===")
    for line in record[:3]:
        print(line)

    print("\n=== 검색 테스트: 소유주 '김철수' ===")
    print(find_by_owner_text(record, "김철수"))