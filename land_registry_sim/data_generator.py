"""
data_generator.py

가상의 조선시대 마을 필지 데이터를 생성한다.
주의: 이 데이터는 실제 조선시대 정밀 사료가 아니라, 세 가지 기록 방식
(양안식 / 데프테리식 / 어린도책식)을 비교하기 위해 만든 예시 데이터다.
실제 자평서에는 이 점을 반드시 명시할 것.

각 필지(Parcel)는 다음 정보를 갖는다:
- id: 필지 고유 번호 (자호 개념)
- owner: 소유주 이름
- grade: 토지 등급 (상/중/하)
- area: 결부수 (임의 단위, 정수)
- x, y, w, h: 캔버스 상 좌표와 크기 (어린도책 시각화용 격자 배치)
- neighbors: 인접한 필지 id 목록 (사표 개념 - 동서남북 경계)
"""

import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class Parcel:
    id: int
    owner: str
    grade: str          # "상" | "중" | "하"
    area: int           # 결부수 (임의 단위)
    x: int
    y: int
    w: int
    h: int
    neighbors: List[int] = field(default_factory=list)


# 등급별 대략적인 세액 계수 (임의 설정 - 실제 결부제 세율이 아님)
GRADE_TAX_RATE = {"상": 3, "중": 2, "하": 1}

OWNER_POOL = [
    "김철수", "이영희", "박민수", "정순자", "최영진",
    "강태호", "윤서연", "임재훈", "한도윤", "오지혜",
    "장현우", "송미경", "권순영", "배준호", "노유진",
]


def generate_village(n_parcels: int = 64, grid_cols: int = 8, seed: int = 42) -> List[Parcel]:
    """
    n_parcels개의 필지를 grid_cols x (n_parcels/grid_cols) 격자 형태로 생성한다.
    격자로 배치하는 이유: 어린도책의 '물고기 비늘처럼 촘촘히 붙은' 필지 배열을
    단순화해서 재현하기 위함. 실제로는 필지 모양이 불규칙하지만,
    이 시뮬레이션에서는 비교의 편의를 위해 격자를 사용한다.
    """
    random.seed(seed)
    cell_size = 40
    parcels: List[Parcel] = []

    for i in range(n_parcels):
        row = i // grid_cols
        col = i % grid_cols
        grade = random.choices(["상", "중", "하"], weights=[2, 5, 3])[0]
        area = random.randint(5, 40)
        parcel = Parcel(
            id=i + 1,
            owner=random.choice(OWNER_POOL),
            grade=grade,
            area=area,
            x=col * cell_size,
            y=row * cell_size,
            w=cell_size,
            h=cell_size,
        )
        parcels.append(parcel)

    # 인접 필지(사표) 계산: 격자 상에서 상하좌우로 붙어있는 필지 id를 채운다
    n_rows = (n_parcels + grid_cols - 1) // grid_cols
    for i, p in enumerate(parcels):
        row = i // grid_cols
        col = i % grid_cols
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < n_rows and 0 <= nc < grid_cols:
                nidx = nr * grid_cols + nc
                if nidx < n_parcels:
                    p.neighbors.append(parcels[nidx].id)

    return parcels


def tax_of(parcel: Parcel) -> int:
    """등급과 결부수를 바탕으로 임의 세액을 계산한다 (실제 세율 아님, 데모용)."""
    return parcel.area * GRADE_TAX_RATE[parcel.grade]


if __name__ == "__main__":
    village = generate_village()
    print(f"생성된 필지 수: {len(village)}")
    print("예시 필지 3개:")
    for p in village[:3]:
        print(f"  {p}")