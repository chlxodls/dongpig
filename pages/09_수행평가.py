
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pydeck as pdk
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="전국 범죄 통계 분석",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. 다크모드 설정
# ==========================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

with st.sidebar:
    st.title("⚙️ 화면 설정")

    st.session_state.dark_mode = st.toggle(
        "🌙 다크모드",
        value=st.session_state.dark_mode
    )

dark = st.session_state.dark_mode

if dark:
    bg = "#0E1117"
    panel = "#1B2330"
    fg = "#FFFFFF"
    grid_color = "#3A4655"
    muted = "#AAB7C4"
else:
    bg = "#FFFFFF"
    panel = "#F1F5F9"
    fg = "#172033"
    grid_color = "#D1D5DB"
    muted = "#64748B"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg};
        color: {fg};
    }}

    [data-testid="stHeader"] {{
        background-color: {bg};
    }}

    [data-testid="stSidebar"] {{
        background-color: {panel};
    }}

    [data-testid="stMetric"] {{
        background-color: {panel};
        padding: 15px;
        border-radius: 12px;
        border: 1px solid {grid_color};
    }}

    [data-testid="stDataFrame"] {{
        background-color: {panel};
    }}

    h1, h2, h3, p, label {{
        color: {fg};
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# Matplotlib 한글 폰트
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

# ==========================================
# 3. CSV 자동 불러오기
# ==========================================

st.title("📊 전국 범죄 통계 분석 시스템")

st.caption(
    "경찰청 범죄 발생 지역별 통계 데이터 분석 대시보드"
)

file_name = "경찰청_범죄 발생 지역별 통계_20251231.csv"

current_dir = Path(__file__).resolve().parent
csv_path = current_dir.parent / file_name

if not csv_path.exists():
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "GitHub 프로젝트 최상위 폴더에 "
        "경찰청_범죄 발생 지역별 통계_20251231.csv "
        "파일을 넣어주세요."
    )
    st.stop()

df = None

for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
    try:
        df = pd.read_csv(
            csv_path,
            encoding=encoding
        )
        break
    except UnicodeDecodeError:
        continue

if df is None:
    st.error("CSV 파일 인코딩을 확인할 수 없습니다.")
    st.stop()

required_cols = ["범죄대분류", "범죄중분류"]

if not all(col in df.columns for col in required_cols):
    st.error("CSV 파일의 컬럼 구성이 올바르지 않습니다.")
    st.stop()

st.success("범죄 통계 데이터 자동 로드 완료!")

# ==========================================
# 4. 데이터 전처리
# ==========================================

area_cols = list(df.columns[2:])

for col in area_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# 외국 지역은 국내 분석에서 제외
domestic_cols = [
    col for col in area_cols
    if not col.startswith("외국")
]

if not domestic_cols:
    st.error("국내 지역 데이터가 없습니다.")
    st.stop()

df["전체합계"] = df[domestic_cols].sum(axis=1)

region_total = (
    df[domestic_cols]
    .sum()
    .sort_values(ascending=False)
)

crime_type = (
    df.groupby("범죄대분류")["전체합계"]
    .sum()
    .sort_values(ascending=False)
)

subcrime_total = (
    df.groupby("범죄중분류")["전체합계"]
    .sum()
    .sort_values(ascending=False)
)

total_crime = int(region_total.sum())

# ==========================================
# 5. 공통 그래프 함수
# ==========================================

def draw_bar_chart(data, title, xlabel, ylabel):

    data = data.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 5))

    fig.patch.set_facecolor(bg)
    ax.set_facecolor(panel)

    colors = ["white"] * len(data)

    if len(data) > 0:
        colors[0] = "#E53935"
        colors[-1] = "#87CEEB"

    ax.bar(
        data.index.astype(str),
        data.values,
        color=colors,
        edgecolor=grid_color,
        linewidth=0.8
    )

    ax.set_title(
        title,
        color=fg,
        fontsize=15,
        pad=15
    )

    ax.set_xlabel(xlabel, color=fg)
    ax.set_ylabel(ylabel, color=fg)

    ax.tick_params(
        axis="x",
        colors=fg,
        rotation=45
    )

    ax.tick_params(axis="y", colors=fg)

    for spine in ax.spines.values():
        spine.set_color(grid_color)

    ax.grid(
        axis="y",
        color=grid_color,
        alpha=0.3
    )

    ax.set_axisbelow(True)

    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


# ==========================================
# 6. 상단 통계 카드
# ==========================================

st.header("📌 전국 범죄 통계 요약")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "전체 범죄 발생 건수",
    f"{total_crime:,}건"
)

c2.metric(
    "분석 지역 수",
    f"{len(domestic_cols)}곳"
)

c3.metric(
    "범죄 유형 수",
    f"{df['범죄대분류'].nunique()}개"
)

c4.metric(
    "세부 범죄 유형 수",
    f"{df['범죄중분류'].nunique()}개"
)

st.divider()

# ==========================================
# 7. 전국 범죄 발생 지도
# ==========================================

st.header("🗺️ 전국 범죄 발생 지도")

st.caption(
    "지역별 범죄 발생 건수를 시도 단위로 합산한 지도입니다. "
    "원형이 클수록 발생 건수가 많습니다."
)

# 시도별 대표 좌표
province_coords = {
    "서울": (37.5665, 126.9780),
    "부산": (35.1796, 129.0756),
    "대구": (35.8714, 128.6014),
    "인천": (37.4563, 126.7052),
    "광주": (35.1595, 126.8526),
    "대전": (36.3504, 127.3845),
    "울산": (35.5384, 129.3114),
    "세종시": (36.4800, 127.2890),
    "경기도": (37.4138, 127.5183),
    "강원도": (37.8228, 128.1555),
    "충북": (36.6357, 127.4914),
    "충남": (36.6588, 126.6728),
    "전북": (35.7175, 127.1530),
    "전남": (34.8679, 126.9910),
    "경북": (36.4919, 128.8889),
    "경남": (35.4606, 128.2132),
    "제주": (33.4996, 126.5312)
}

province_data = {}

for col in domestic_cols:

    province = col.split()[0]

    if province in province_coords:

        province_data[province] = (
            province_data.get(province, 0)
            + int(df[col].sum())
        )

map_df = pd.DataFrame([
    {
        "지역": name,
        "위도": province_coords[name][0],
        "경도": province_coords[name][1],
        "범죄건수": count
    }
    for name, count in province_data.items()
])

if not map_df.empty:

    highest = map_df["범죄건수"].max()
    lowest = map_df["범죄건수"].min()

    def marker_color(value):

        if value == highest:
            return [229, 57, 53, 220]

        elif value == lowest:
            return [135, 206, 235, 220]

        return [255, 255, 255, 190]

    map_df["색상"] = map_df["범죄건수"].apply(
        marker_color
    )

    map_df["반지름"] = (
        5000
        + map_df["범죄건수"] /
        max(highest, 1) * 20000
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[경도, 위도]",
        get_radius="반지름",
        get_fill_color="색상",
        get_line_color=[100, 100, 100],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=36.3,
        longitude=127.8,
        zoom=5.2,
        pitch=0
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=(
            "https://basemaps.cartocdn.com/gl/"
            + ("dark-matter" if dark else "positron")
            + "-gl-style/style.json"
        ),
        tooltip={
            "html": (
                "<b>{지역}</b><br/>"
                "범죄 발생: {범죄건수}건"
            ),
            "style": {
                "backgroundColor": "#222222",
                "color": "white"
            }
        }
    )

    st.pydeck_chart(
        deck,
        use_container_width=True
    )

    st.caption(
        "🔴 최다 발생 지역 | 🔵 최저 발생 지역 | ⚪ 기타 지역"
    )

st.divider()

# ==========================================
# 8. 범죄 통계 TOP 5 자동 순위
# ==========================================

st.header("🏆 범죄 통계 TOP 5")

tab1, tab2, tab3 = st.tabs([
    "지역별 TOP 5",
    "범죄 유형 TOP 5",
    "세부 범죄 TOP 5"
])

with tab1:

    top_region = region_total.head(5)

    for i, (name, value) in enumerate(
        top_region.items(), start=1
    ):

        st.write(
            f"**{i}위. {name}** — {int(value):,}건"
        )

    draw_bar_chart(
        top_region,
        "지역별 범죄 발생 TOP 5",
        "지역",
        "발생 건수"
    )

with tab2:

    top_crime = crime_type.head(5)

    for i, (name, value) in enumerate(
        top_crime.items(), start=1
    ):

        st.write(
            f"**{i}위. {name}** — {int(value):,}건"
        )

    draw_bar_chart(
        top_crime,
        "범죄 유형 TOP 5",
        "범죄 유형",
        "발생 건수"
    )

with tab3:

    top_subcrime = subcrime_total.head(5)

    for i, (name, value) in enumerate(
        top_subcrime.items(), start=1
    ):

        st.write(
            f"**{i}위. {name}** — {int(value):,}건"
        )

    draw_bar_chart(
        top_subcrime,
        "세부 범죄 TOP 5",
        "범죄 유형",
        "발생 건수"
    )

st.divider()

# ==========================================
# 9. 지역별 범죄 히트맵
# ==========================================

st.header("🌡️ 지역별 범죄 히트맵")

st.caption(
    "지역별 범죄 유형의 발생 건수를 색상으로 비교합니다."
)

# 상위 지역 20곳
heat_regions = region_total.head(20).index.tolist()

# 상위 범죄 유형 10개
heat_crimes = crime_type.head(10).index.tolist()

heat_data = (
    df.groupby("범죄대분류")[heat_regions]
    .sum()
    .loc[heat_crimes]
)

fig, ax = plt.subplots(
    figsize=(16, 7)
)

fig.patch.set_facecolor(bg)
ax.set_facecolor(panel)

im = ax.imshow(
    heat_data.values,
    cmap="magma",
    aspect="auto"
)

ax.set_xticks(range(len(heat_regions)))
ax.set_xticklabels(
    heat_regions,
    rotation=60,
    ha="right",
    color=fg,
    fontsize=8
)

ax.set_yticks(range(len(heat_crimes)))
ax.set_yticklabels(
    heat_crimes,
    color=fg
)

ax.set_title(
    "지역별 범죄 유형 히트맵",
    color=fg,
    fontsize=15,
    pad=15
)

ax.set_xlabel("지역", color=fg)
ax.set_ylabel("범죄 유형", color=fg)

colorbar = fig.colorbar(im, ax=ax)
colorbar.set_label(
    "범죄 발생 건수",
    color=fg
)
colorbar.ax.yaxis.set_tick_params(color=fg)
plt.setp(
    colorbar.ax.get_yticklabels(),
    color=fg
)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.info(
    "히트맵에서 밝은 색상일수록 해당 범죄 유형의 "
    "발생 건수가 많다는 의미입니다."
)

st.divider()

# ==========================================
# 10. 범죄 유형별 전체 분석
# ==========================================

st.header("📊 범죄 유형별 발생 현황")

draw_bar_chart(
    crime_type,
    "전국 범죄 유형별 발생 건수",
    "범죄 유형",
    "발생 건수"
)

# ==========================================
# 11. 지역별 범죄 발생 분석
# ==========================================

st.header("📍 지역별 범죄 발생 TOP 10")

top10 = region_total.head(10)

draw_bar_chart(
    top10,
    "전국 지역별 범죄 발생 TOP 10",
    "지역",
    "발생 건수"
)

# ==========================================
# 12. 서울 자치구별 분석
# ==========================================

st.header("🏙️ 서울 자치구별 범죄 발생 현황")

seoul_cols = [
    col for col in domestic_cols
    if col.startswith("서울 ")
]

seoul_total = (
    df[seoul_cols]
    .sum()
    .sort_values(ascending=False)
)

if not seoul_total.empty:

    draw_bar_chart(
        seoul_total,
        "서울 자치구별 범죄 발생 현황",
        "자치구",
        "발생 건수"
    )

# ==========================================
# 13. 원하는 지역 상세 분석
# ==========================================

st.header("🔎 지역별 상세 분석")

selected_region = st.selectbox(
    "분석할 지역을 선택하세요.",
    sorted(domestic_cols)
)

region_data = (
    df[
        [
            "범죄대분류",
            "범죄중분류",
            selected_region
        ]
    ]
    .sort_values(
        by=selected_region,
        ascending=False
    )
)

st.metric(
    f"{selected_region} 범죄 발생 건수",
    f"{int(df[selected_region].sum()):,}건"
)

draw_bar_chart(
    region_data.head(15).set_index(
        "범죄중분류"
    )[selected_region],
    f"{selected_region} 세부 범죄 TOP 15",
    "범죄 유형",
    "발생 건수"
)

with st.expander("상세 데이터 확인"):
    st.dataframe(
        region_data,
        use_container_width=True
    )

# ==========================================
# 14. 자동 분석 결과
# ==========================================

st.header("📝 최종 분석 결과")

st.write(
    f"""
    - 전체 국내 범죄 발생 건수는 **{total_crime:,}건**입니다.
    - 가장 많은 범죄가 발생한 지역은
      **{region_total.index[0]}**이며,
      **{int(region_total.iloc[0]):,}건**입니다.
    - 가장 많이 발생한 범죄 유형은
      **{crime_type.index[0]}**이며,
      **{int(crime_type.iloc[0]):,}건**입니다.
    - 가장 많이 발생한 세부 범죄는
      **{subcrime_total.index[0]}**이며,
      **{int(subcrime_total.iloc[0]):,}건**입니다.
    """
)

st.success("전국 범죄 통계 분석이 완료되었습니다!")

st.caption(
    "자료: 경찰청 범죄 발생 지역별 통계_20251231.csv | "
    "분석 도구: Python, Pandas, Matplotlib, PyDeck"
)
