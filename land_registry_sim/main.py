"""
main.py

전체 시뮬레이션 실행 진입점.
1) 가상 마을 데이터 생성
2) 세 가지 기록 방식(양안식/데프테리식/어린도책식)으로 변환
3) 동일 질의에 대한 벤치마크 실행
4) 어린도책 스타일 시각화 생성

각 단계는 독립된 모듈(data_generator.py, format_*.py, benchmark.py,
visualize.py)에 있으며, 이 파일은 그것들을 순서대로 호출만 한다.
"""

from data_generator import generate_village
from format_yangan import build_yangan_record
from format_defteri import build_defteri_record, aggregate_by_village
from format_eorindochaek import build_eorindochaek_record
from benchmark import run_benchmark
from visualize import draw_village


def main():
    print("=" * 60)
    print("1. 가상 마을 데이터 생성")
    print("=" * 60)
    village = generate_village(n_parcels=64, grid_cols=8)
    print(f"필지 {len(village)}개 생성 완료.\n")

    print("=" * 60)
    print("2. 세 가지 기록 방식으로 변환")
    print("=" * 60)
    yangan = build_yangan_record(village)
    defteri = build_defteri_record(village)
    eorin = build_eorindochaek_record(village)
    print("양안식(텍스트) 1건 예시:")
    print(f"  {yangan[0]}\n")
    print("데프테리식(표) 1건 예시:")
    print(f"  {defteri[0]}\n")
    print("어린도책식(표+좌표) 1건 예시:")
    print(f"  {eorin[0]}\n")

    print("=" * 60)
    print("3. 마을 전체 집계 (도총 개념, 데프테리식 활용)")
    print("=" * 60)
    for grade, stats in aggregate_by_village(defteri).items():
        print(f"  {grade}등: 필지 {stats['count']}개, "
              f"면적 합 {stats['total_area']}, 세액 합 {stats['total_tax']}")
    print()

    print("=" * 60)
    print("4. 벤치마크: 동일 질의를 세 방식으로 처리했을 때 비교")
    print("=" * 60)
    run_benchmark(n_parcels=500, n_repeat=200)

    print("=" * 60)
    print("5. 어린도책 스타일 시각화 생성")
    print("=" * 60)
    draw_village(village, save_path="eorindochaek_style_map.png")


if __name__ == "__main__":
    main()