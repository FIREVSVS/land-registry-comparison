"""
format_eorindochaek.py

'어린도책식' 기록 방식: 중국 어린도책(魚鱗圖冊)처럼 표 구조에 더해
필지의 공간 좌표(그림/도형 요소)까지 함께 기록한다.

데프테리식(format_defteri.py)이 표를 통해 속성 검색을 빠르게 만들었다면,
어린도책식은 여기에 '공간적 위치 관계'를 더해서 데프테리식으로도
할 수 없는 질의(예: 특정 지점 주변 필지 찾기, 두 필지가 실제로
맞닿아 있는지 좌표로 검증하기)를 가능하게 한다.
"""

from typing import List, Dict, Tuple
from data_generator import Parcel, tax_of


def build_eorindochaek_record(parcels: List[Parcel]) -> List[Dict]:
    """마을 전체를 표+좌표 구조로 변환한다."""
    return [
        {
            "id": p.id,
            "owner": p.owner,
            "grade": p.grade,
            "area": p.area,
            "tax": tax_of(p),
            "neighbors": p.neighbors,
            "x": p.x,
            "y": p.y,
            "w": p.w,
            "h": p.h,
        }
        for p in parcels
    ]


# ---------------------------------------------------------------------
# 좌표를 활용해야만 가능한 질의들.
# 데프테리식 표만으로는 "공간적으로 가깝다"는 개념 자체가 없어서
# 이런 질의를 처리할 수 없다는 게 핵심 비교 포인트다.
# ---------------------------------------------------------------------

def find_parcel_at_point(record: List[Dict], px: int, py: int) -> Dict:
    """특정 좌표(px, py)가 어느 필지 안에 있는지 찾는다. (지도 클릭 조회에 해당)"""
    for row in record:
        if row["x"] <= px < row["x"] + row["w"] and row["y"] <= py < row["y"] + row["h"]:
            return row
    return None


def find_parcels_within_radius(record: List[Dict], center_id: int, radius: float) -> List[Dict]:
    """
    특정 필지 중심으로부터 반경(radius) 이내에 있는 모든 필지를 찾는다.
    이건 순수 속성 검색(데프테리식)으로는 원천적으로 불가능하고,
    좌표가 있어야만 계산할 수 있는 질의다.
    """
    center = next((r for r in record if r["id"] == center_id), None)
    if center is None:
        return []
    cx = center["x"] + center["w"] / 2
    cy = center["y"] + center["h"] / 2

    result = []
    for row in record:
        if row["id"] == center_id:
            continue
        rx = row["x"] + row["w"] / 2
        ry = row["y"] + row["h"] / 2
        dist = ((rx - cx) ** 2 + (ry - cy) ** 2) ** 0.5
        if dist <= radius:
            result.append(row)
    return result


def verify_adjacency_by_coordinates(record: List[Dict], id_a: int, id_b: int) -> bool:
    """
    두 필지가 실제로 좌표상 맞닿아 있는지(사표 관계가 실제 공간과 일치하는지)
    검증한다. 양안식/데프테리식은 '사표'를 텍스트/필드로 "주장"만 할 뿐,
    실제 그 주장이 기하학적으로 맞는지 검증할 방법이 없다.
    어린도책식은 좌표가 있으므로 이 검증이 가능하다 -- 이는 실제로
    기록의 정확성을 사후 검증할 수 있다는 실질적 이점으로 이어진다.
    """
    a = next((r for r in record if r["id"] == id_a), None)
    b = next((r for r in record if r["id"] == id_b), None)
    if a is None or b is None:
        return False

    touching_x = (a["x"] + a["w"] == b["x"]) or (b["x"] + b["w"] == a["x"])
    same_row = a["y"] == b["y"]
    touching_y = (a["y"] + a["h"] == b["y"]) or (b["y"] + b["h"] == a["y"])
    same_col = a["x"] == b["x"]

    return (touching_x and same_row) or (touching_y and same_col)


if __name__ == "__main__":
    from data_generator import generate_village

    village = generate_village()
    record = build_eorindochaek_record(village)

    print("=== 어린도책식 기록 예시 (앞 3건) ===")
    for row in record[:3]:
        print(row)

    print("\n=== 좌표 검증: 필지 1과 2가 실제로 맞닿아 있는가? ===")
    print(verify_adjacency_by_coordinates(record, 1, 2))

    print("\n=== 반경 검색: 필지 1 주변 50 이내 필지 ===")
    nearby = find_parcels_within_radius(record, 1, 50)
    print([r["id"] for r in nearby])