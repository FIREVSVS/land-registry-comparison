"""
benchmark.py

세 가지 기록 방식(양안식 / 데프테리식 / 어린도책식)에 동일한 질의를 던져서
1) 실행시간, 2) 지원 가능 여부(가능/불가능)를 비교한다.

주의: 이 필지 규모(수백 개)에서는 실행시간 차이가 사람이 체감할 정도로
크지는 않다. 이 벤치마크의 목적은 "속도 자체"보다 "구조화 정도에 따라
같은 질문을 처리하는 코드의 형태와 가능 여부가 달라진다"는 걸
보여주는 데 있다. 자평서에는 이 점을 분명히 밝힐 것.
"""

import timeit

from data_generator import generate_village
from format_yangan import (
    build_yangan_record,
    find_by_owner_text,
    sum_tax_by_grade_text,
    find_adjacent_parcels_text,
)
from format_defteri import (
    build_defteri_record,
    find_by_owner_table,
    sum_tax_by_grade_table,
    find_adjacent_parcels_table,
)
from format_eorindochaek import (
    build_eorindochaek_record,
    find_parcels_within_radius,
    verify_adjacency_by_coordinates,
)


def run_benchmark(n_parcels: int = 500, n_repeat: int = 200):
    village = generate_village(n_parcels=n_parcels, grid_cols=20)

    yangan_record = build_yangan_record(village)
    defteri_record = build_defteri_record(village)
    eorin_record = build_eorindochaek_record(village)

    print(f"필지 수: {n_parcels}개, 반복 횟수: {n_repeat}회\n")

    # -------------------------------------------------------------
    # 질의 1: 특정 소유주의 필지 찾기
    # -------------------------------------------------------------
    print("[질의 1] 소유주 '김철수'의 모든 필지 찾기")
    t_yangan = timeit.timeit(
        lambda: find_by_owner_text(yangan_record, "김철수"), number=n_repeat
    )
    t_defteri = timeit.timeit(
        lambda: find_by_owner_table(defteri_record, "김철수"), number=n_repeat
    )
    print(f"  양안식(문자열 매칭)  : {t_yangan:.5f}초")
    print(f"  데프테리식(표 필터)  : {t_defteri:.5f}초")
    print(f"  → 배율: 양안식이 데프테리식보다 약 {t_yangan / t_defteri:.1f}배 느림\n")

    # -------------------------------------------------------------
    # 질의 2: 등급별 세액 합계
    # -------------------------------------------------------------
    print("[질의 2] '중'등급 필지 세액 합계 구하기")
    t_yangan2 = timeit.timeit(
        lambda: sum_tax_by_grade_text(yangan_record, "중"), number=n_repeat
    )
    t_defteri2 = timeit.timeit(
        lambda: sum_tax_by_grade_table(defteri_record, "중"), number=n_repeat
    )
    print(f"  양안식(정규식 재파싱): {t_yangan2:.5f}초")
    print(f"  데프테리식(필드 합산): {t_defteri2:.5f}초")
    print(f"  → 배율: 양안식이 데프테리식보다 약 {t_yangan2 / t_defteri2:.1f}배 느림\n")

    # -------------------------------------------------------------
    # 질의 3: 인접 필지 조회 (사표)
    # -------------------------------------------------------------
    print("[질의 3] 필지 1번의 인접 필지(사표) 조회")
    t_yangan3 = timeit.timeit(
        lambda: find_adjacent_parcels_text(yangan_record, 1), number=n_repeat
    )
    t_defteri3 = timeit.timeit(
        lambda: find_adjacent_parcels_table(defteri_record, 1), number=n_repeat
    )
    print(f"  양안식(정규식 재파싱): {t_yangan3:.5f}초")
    print(f"  데프테리식(필드 조회): {t_defteri3:.5f}초")
    print(f"  → 배율: 양안식이 데프테리식보다 약 {t_yangan3 / t_defteri3:.1f}배 느림\n")

    # -------------------------------------------------------------
    # 질의 4: 공간 반경 검색 -- 양안식/데프테리식은 원천적으로 불가능
    # -------------------------------------------------------------
    print("[질의 4] 필지 1번 반경 100 이내 필지 찾기 (공간 질의)")
    print("  양안식      : 지원 불가 (좌표 정보 자체가 없음)")
    print("  데프테리식  : 지원 불가 (좌표 정보 자체가 없음)")
    t_eorin4 = timeit.timeit(
        lambda: find_parcels_within_radius(eorin_record, 1, 100), number=n_repeat
    )
    print(f"  어린도책식(좌표 기반): {t_eorin4:.5f}초 -- 유일하게 처리 가능\n")

    # -------------------------------------------------------------
    # 질의 5: 사표 기록이 실제 공간과 일치하는지 검증
    # -------------------------------------------------------------
    print("[질의 5] 필지 1-2가 실제로 맞닿아 있는지 좌표로 검증")
    print("  양안식/데프테리식: 검증 불가 (기록을 '주장'만 할 뿐 확인할 방법 없음)")
    result = verify_adjacency_by_coordinates(eorin_record, 1, 2)
    print(f"  어린도책식(좌표 대조): 검증 가능 → 결과: {result}\n")


if __name__ == "__main__":
    run_benchmark()