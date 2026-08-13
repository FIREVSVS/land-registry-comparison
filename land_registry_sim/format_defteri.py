"""
format_defteri.py

'데프테리식' 기록 방식: 오스만 타흐리르 데프테리(TD 373 아인탑 리바 사례)처럼
필지 정보를 항목별 열(column)을 가진 표 구조로 저장한다.

핵심 차이: 양안식은 문장 안에 정보가 '섞여' 있어서 다시 파싱해야 하지만,
데프테리식은 필드가 이미 분리되어 있어 필터링·집계가 훨씬 단순해진다.
실제 아인탑 데프테리도 hane(가구)·çift(경작단위)·bennak 등 항목별로
집계표를 만들었다는 점을 재현한 것.
"""

from typing import List, Dict
from data_generator import Parcel, tax_of


def build_defteri_record(parcels: List[Parcel]) -> List[Dict]:
    """마을 전체를 표(딕셔너리 리스트) 형태로 변환한다."""
    return [
        {
            "id": p.id,
            "owner": p.owner,
            "grade": p.grade,
            "area": p.area,
            "tax": tax_of(p),
            "neighbors": p.neighbors,
        }
        for p in parcels
    ]


# ---------------------------------------------------------------------
# 표 구조를 활용한 질의 함수들.
# 양안식(format_yangan.py)의 동일 기능 함수들과 줄 수·복잡도를 비교할 것.
# ---------------------------------------------------------------------

def find_by_owner_table(record: List[Dict], owner_name: str) -> List[Dict]:
    """소유주 이름으로 필지를 찾는다. 필드가 분리되어 있어 단순 비교 한 줄로 끝난다."""
    return [row for row in record if row["owner"] == owner_name]


def sum_tax_by_grade_table(record: List[Dict], grade: str) -> int:
    """등급별 세액 합계. tax 필드가 이미 계산되어 저장되어 있으므로 합산만 하면 된다."""
    return sum(row["tax"] for row in record if row["grade"] == grade)


def find_adjacent_parcels_table(record: List[Dict], parcel_id: int) -> List[int]:
    """특정 필지의 인접 필지 id 목록. neighbors 필드를 바로 조회하면 된다."""
    for row in record:
        if row["id"] == parcel_id:
            return row["neighbors"]
    return []


def aggregate_by_village(record: List[Dict]) -> Dict:
    """
    마을 전체 집계 (도총圖總 개념 재현).
    아인탑 데프테리가 hane, çift, bennak 등을 항목별로 전부 세어
    리바 전체 집계를 냈던 것처럼, 등급별 필지 수/면적/세액 합계를 구한다.
    """
    summary = {}
    for row in record:
        g = row["grade"]
        if g not in summary:
            summary[g] = {"count": 0, "total_area": 0, "total_tax": 0}
        summary[g]["count"] += 1
        summary[g]["total_area"] += row["area"]
        summary[g]["total_tax"] += row["tax"]
    return summary


if __name__ == "__main__":
    from data_generator import generate_village

    village = generate_village()
    record = build_defteri_record(village)

    print("=== 데프테리식 기록 예시 (앞 3건) ===")
    for row in record[:3]:
        print(row)

    print("\n=== 검색 테스트: 소유주 '김철수' ===")
    print(find_by_owner_table(record, "김철수"))

    print("\n=== 마을 전체 집계 (도총 개념) ===")
    for grade, stats in aggregate_by_village(record).items():
        print(f"  {grade}등: {stats}")