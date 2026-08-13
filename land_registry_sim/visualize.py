"""
visualize.py

어린도책(魚鱗圖冊) 스타일로 필지를 시각화한다.
실제 어린도책은 필지를 손으로 그린 도형(주로 사각형/부정형)으로 배치하고
그 안이나 옆에 자호·소유주·면적 등을 문자로 병기했다.
이 모듈은 그 '그림+표 하이브리드' 구조를 matplotlib으로 재현한다.

등급(상/중/하)별로 색을 다르게 칠해서, 그림만 봐도 토지 등급 분포를
한눈에 파악할 수 있게 한다 -- 이게 순수 텍스트(양안식)로는
불가능한, 시각화가 주는 직관적 이점이다.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm

from data_generator import generate_village, tax_of

# 한글이 네모(□)로 깨지지 않도록 시스템에 설치된 CJK 폰트를 지정한다.
# (VSCode 로컬 환경에서 실행 시, 설치된 한글 폰트 이름으로 바꿔야 할 수 있음.
#  예: "Malgun Gothic"(윈도우), "AppleGothic"(맥) 등)
_KOREAN_FONT_CANDIDATES = ["Noto Sans CJK KR", "NanumGothic", "Malgun Gothic", "AppleGothic"]
for _font_name in _KOREAN_FONT_CANDIDATES:
    if any(_font_name in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = _font_name
        break
plt.rcParams["axes.unicode_minus"] = False

GRADE_COLOR = {"상": "#f4a261", "중": "#e9c46a", "하": "#a8dadc"}


def draw_village(parcels, save_path: str = None, show_labels: bool = True):
    fig, ax = plt.subplots(figsize=(12, 12))

    for p in parcels:
        color = GRADE_COLOR[p.grade]
        rect = patches.Rectangle(
            (p.x, p.y), p.w, p.h,
            linewidth=1, edgecolor="black", facecolor=color
        )
        ax.add_patch(rect)

        if show_labels:
            label = f"{p.id}\n{p.owner}\n{p.grade}/{tax_of(p)}"
            ax.text(
                p.x + p.w / 2, p.y + p.h / 2, label,
                ha="center", va="center", fontsize=5.5
            )

    max_x = max(p.x + p.w for p in parcels)
    max_y = max(p.y + p.h for p in parcels)
    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)
    ax.invert_yaxis()  # 위에서 아래로 읽히도록 (지도/문서 관례)
    ax.set_aspect("equal")
    ax.set_title("어린도책식 시각화 예시 (가상 데이터)\n"
                  "숫자=필지ID, 이름=소유주, 색=등급, 뒷숫자=세액", fontsize=11)

    # 범례
    legend_patches = [
        patches.Patch(color=GRADE_COLOR[g], label=f"{g}등") for g in ["상", "중", "하"]
    ]
    ax.legend(handles=legend_patches, loc="upper right")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"저장됨: {save_path}")
    else:
        plt.show()


if __name__ == "__main__":
    village = generate_village(n_parcels=64, grid_cols=8)
    draw_village(village, save_path="eorindochaek_style_map.png")