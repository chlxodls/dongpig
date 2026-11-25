
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    st.title("⚙️ 설정")

    st.session_state.dark_mode = st.toggle(
        "🌙 다크모드",
        value=st.session_state.dark_mode
    )

dark = st.session_state.dark_mode

if dark:
    BG = "#0E1117"
    PANEL = "#1B2330"
    TEXT = "#FFFFFF"
    GRID = "#394554"
    TEMPLATE = "plotly_dark"
else:
    BG = "#FFFFFF"
    PANEL = "#F1F5F9"
    TEXT = "#172033"
    GRID = "#D1D5DB"
    TEMPLATE = "plotly_white"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    [data-testid="stSidebar"] {{
        background-color: {PANEL};
    }}

    [data-testid="stMetric"] {{
        background-color: {PANEL};
        padding: 15px;
        border-radius: 12px;
        border: 1px solid {GRID};
    }}

    h1, h2, h3, p, label {{
        color: {TEXT};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 전국 범죄 통계 분석 시스템")

st.caption(
    "경찰청 범죄 발생 지역별 통계 | Pandas 데이터 분석"
)

# ==========================================
# 3. CSV 자동 로드
# ==========================================

file_name = "경찰청_범죄 발생 지역별 통계_20251231.csv"

current_dir = Path(__file__).resolve().parent

possible_paths = [
    current_dir.parent / file_name,
    current_dir / file_name,
    Path.cwd() / file_name
]

csv_path = next(
    (p for p in possible_paths if p.exists()),
    None
)

if csv_path is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "GitHub 프로젝트 최상위 폴더에 "
        "경찰청_범죄 발생 지역별 통계_20251231.csv "
        "파일을 업로드해 주세요."
    )
    st.stop()


@st.cache_data
def load_data(path, modified_time):

    encodings = [
        "cp949",
        "utf-8-sig",
        "euc-kr"
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                path,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인할 수 없습니다.")


try:
    df = load_data(
        str(csv_path),
        csv_path.stat().st_mtime
    )

except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()


# ==========================================
# 4. 데이터 전처리
# ==========================================

required_cols = [
    "범죄대분류",
    "범죄중분류"
]

if not all(col in df.columns for col in required_cols):
    st.error("CSV 컬럼 구성이 올바르지 않습니다.")
    st.stop()

area_cols = list(df.columns[2:])

# 지역별 숫자 변환
for col in area_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# 외국 지역 제외
domestic_cols = [
    col for col in area_cols
    if not col.startswith("외국")
]

if not domestic_cols:
    st.error("국내 지역 데이터가 없습니다.")
    st.stop()

# 전체 범죄 발생 건수
df["전체합계"] = df[domestic_cols].sum(axis=1)

# 지역별 합계
region_total = (
    df[domestic_cols]
    .sum()
    .sort_values(ascending=False)
)

# 범죄 대분류별 합계
crime_type = (
    df.groupby("범죄대분류")["전체합계"]
    .sum()
    .sort_values(ascending=False)
)

# 범죄 중분류별 합계
subcrime_total = (
    df.groupby("범죄중분류")["전체합계"]
    .sum()
    .sort_values(ascending=False)
)

total_crime = int(region_total.sum())

# ==========================================
# 5. 공통 그래프 함수
# ==========================================

def draw_bar_chart(data, title):

    data = data.sort_values(
        ascending=False
    )

    colors = ["white"] * len(data)

    if len(data) > 0:
        colors[0] = "#E53935"
        colors[-1] = "#87CEEB"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data.index.astype(str),
            y=data.values,
            marker_color=colors,
            marker_line_color=GRID,
            marker_line_width=1,
            text=[
                f"{int(v):,}"
                for v in data.values
            ],
            textposition="outside",
            textfont=dict(
                color=TEXT,
                size=11
            )
        )
    )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color=TEXT)
        ),
        template=TEMPLATE,
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(
            family="Malgun Gothic, sans-serif",
            color=TEXT
        ),
        xaxis_title="지역 및 범죄 유형",
        yaxis_title="발생 건수",
        yaxis=dict(
            tickformat=",",
            gridcolor=GRID
        ),
        xaxis=dict(
            gridcolor=GRID,
            tickangle=-40
        ),
        showlegend=False,
        height=480,
        margin=dict(
            t=80,
            b=100,
            l=60,
            r=30
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================
# 6. 상단 통계 카드
# ==========================================

st.header("📌 전국 범죄 통계 요약")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "전체 범죄 발생",
    f"{total_crime:,}건"
)

c2.metric(
    "분석 지역",
    f"{len(domestic_cols)}곳"
)

c3.metric(
    "범죄 대분류",
    f"{df['범죄대분류'].nunique()}개"
)

c4.metric(
    "범죄 중분류",
    f"{df['범죄중분류'].nunique()}개"
)

st.divider()

# ==========================================
# 7. 전국 범죄 발생 지도
# ==========================================

st.header("🗺️ 전국 범죄 발생 지도")

st.caption(
    "시도별 범죄 발생 건수를 합산한 지도입니다. "
    "원형이 클수록 범죄 발생 건수가 많습니다."
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

    def get_color(value):

        if value == highest:
            return [229, 57, 53, 220]

        elif value == lowest:
            return [135, 206, 235, 220]

        return [255, 255, 255, 190]

    map_df["색상"] = map_df["범죄건수"].apply(
        get_color
    )

    map_df["크기"] = (
        4000
        + map_df["범죄건수"] /
        max(highest, 1) * 22000
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[경도, 위도]",
        get_radius="크기",
        get_fill_color="색상",
        get_line_color=[100, 100, 100],
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
            + (
                "dark-matter"
                if dark
                else "positron"
            )
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

else:
    st.warning("지도에 표시할 지역 데이터가 없습니다.")

st.divider()

# ==========================================
# 8. 범죄 통계 TOP 5
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
        top_region.items(),
        start=1
    ):
        st.write(
            f"**{i}위. {name}** "
            f"— {int(value):,}건"
        )

    draw_bar_chart(
        top_region,
        "지역별 범죄 발생 TOP 5"
    )

with tab2:

    top_crime = crime_type.head(5)

    for i, (name, value) in enumerate(
        top_crime.items(),
        start=1
    ):
        st.write(
            f"**{i}위. {name}** "
            f"— {int(value):,}건"
        )

    draw_bar_chart(
        top_crime,
        "범죄 유형 TOP 5"
    )

with tab3:

    top_subcrime = subcrime_total.head(5)

    for i, (name, value) in enumerate(
        top_subcrime.items(),
        start=1
    ):
        st.write(
            f"**{i}위. {name}** "
            f"— {int(value):,}건"
        )

    draw_bar_chart(
        top_subcrime,
        "세부 범죄 TOP 5"
    )

st.divider()

# ==========================================
# 9. 지역별 범죄 히트맵
# ==========================================

st.header("🌡️ 지역별 범죄 히트맵")

st.caption(
    "범죄 유형과 지역별 발생 건수를 색상으로 비교합니다."
)

heat_regions = region_total.head(20).index.tolist()

heat_crimes = crime_type.head(10).index.tolist()

heat_data = (
    df.groupby("범죄대분류")[heat_regions]
    .sum()
    .reindex(heat_crimes)
)

fig = px.imshow(
    heat_data,
    labels={
        "x": "지역",
        "y": "범죄 유형",
        "color": "발생 건수"
    },
    x=heat_regions,
    y=heat_crimes,
    color_continuous_scale="Magma",
    aspect="auto",
    text_auto=","
)

fig.update_layout(
    title="지역별 범죄 유형 히트맵",
    template=TEMPLATE,
    paper_bgcolor=BG,
    plot_bgcolor=PANEL,
    font=dict(
        family="Malgun Gothic, sans-serif",
        color=TEXT
    ),
    height=650,
    xaxis=dict(
        tickangle=-55
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.info(
    "밝은 색상일수록 해당 지역의 범죄 발생 건수가 많습니다."
)

st.divider()

# ==========================================
# 10. 범죄 유형별 분석
# ==========================================

st.header("📊 범죄 유형별 발생 현황")

draw_bar_chart(
    crime_type,
    "전국 범죄 유형별 발생 건수"
)

# ==========================================
# 11. 지역별 범죄 TOP 10
# ==========================================

st.header("📍 지역별 범죄 발생 TOP 10")

draw_bar_chart(
    region_total.head(10),
    "전국 지역별 범죄 발생 TOP 10"
)

# ==========================================
# 12. 서울 자치구 분석
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
        "서울 자치구별 범죄 발생 현황"
    )

# ==========================================
# 13. 지역 상세 분석
# ==========================================

st.header("🔎 지역별 상세 분석")

selected_region = st.selectbox(
    "분석할 지역 선택",
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
    f"{selected_region} 세부 범죄 TOP 15"
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

st.markdown(
    f"""
    ### 전국 범죄 분석 결과

    - 국내 전체 범죄 발생 건수: **{total_crime:,}건**
    - 가장 높은 발생 지역: **{region_total.index[0]}**
    - 해당 지역 발생 건수: **{int(region_total.iloc[0]):,}건**
    - 가장 높은 범죄 유형: **{crime_type.index[0]}**
    - 해당 범죄 발생 건수: **{int(crime_type.iloc[0]):,}건**
    - 가장 많은 세부 범죄: **{subcrime_total.index[0]}**
    - 해당 세부 범죄 발생 건수: **{int(subcrime_total.iloc[0]):,}건**
    """
)

st.success("전국 범죄 통계 분석이 완료되었습니다!")

st.caption(
    "자료: 경찰청 범죄 발생 지역별 통계_20251231.csv"
)

# ==========================================
# 🧠 범죄 통계 자동 분석 및 해석
# ==========================================

st.divider()
st.header("🧠 데이터 기반 자동 분석 결과")
st.caption("경찰청 범죄 발생 지역별 통계 데이터를 바탕으로 분석한 결과입니다.")

# 국내 지역 컬럼만 추출
analysis_region_cols = [
    col for col in df.columns[2:]
    if not str(col).startswith("외국")
]

# 숫자 데이터 변환
for col in analysis_region_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 범죄 유형별 데이터 정리
analysis_df = df.copy()
analysis_df["범죄대분류"] = analysis_df["범죄대분류"].fillna("미분류")
analysis_df["범죄중분류"] = analysis_df["범죄중분류"].fillna("미분류")

# 지역별 총 범죄 발생 건수
region_total = (
    analysis_df[analysis_region_cols]
    .sum()
    .sort_values(ascending=False)
)

# 범죄대분류별 전국 합계
category_total = (
    analysis_df.groupby("범죄대분류")[analysis_region_cols]
    .sum()
    .sum(axis=1)
    .sort_values(ascending=False)
)

# 범죄중분류별 전국 합계
detail_total = (
    analysis_df.groupby("범죄중분류")[analysis_region_cols]
    .sum()
    .sum(axis=1)
    .sort_values(ascending=False)
)

# 전체 발생 건수
national_total = int(region_total.sum())

if national_total > 0 and len(region_total) > 0:

    # 최고·최저 지역
    top_region = region_total.index[0]
    top_region_value = int(region_total.iloc[0])

    # 발생 건수가 0보다 큰 지역만 최저 지역 후보로 사용
    positive_regions = region_total[region_total > 0]

    if len(positive_regions) > 0:
        low_region = positive_regions.index[-1]
        low_region_value = int(positive_regions.iloc[-1])
    else:
        low_region = "확인 불가"
        low_region_value = 0

    # 최다 범죄대분류
    top_category = category_total.index[0]
    top_category_value = int(category_total.iloc[0])
    category_ratio = top_category_value / national_total * 100

    # 최다 범죄중분류
    top_detail = detail_total.index[0]
    top_detail_value = int(detail_total.iloc[0])

    # 상위 5개 지역의 발생 건수 비중
    top5_total = int(region_total.head(5).sum())
    top5_ratio = top5_total / national_total * 100

    # 가장 많이 발생한 지역의 주요 범죄 유형
    region_category = (
        analysis_df.groupby("범죄대분류")[top_region]
        .sum()
        .sort_values(ascending=False)
    )

    dominant_category = region_category.index[0]
    dominant_value = int(region_category.iloc[0])

    # 핵심 지표
    st.subheader("📊 핵심 분석 지표")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "국내 전체 범죄 발생 건수",
        f"{national_total:,}건"
    )

    col2.metric(
        "발생 건수 최다 지역",
        top_region,
        f"{top_region_value:,}건"
    )

    col3.metric(
        "발생 건수 최다 범죄 유형",
        top_category,
        f"{top_category_value:,}건"
    )

    st.divider()

    # 자동 분석 결과 1
    st.subheader("① 지역별 범죄 발생 분석")

    st.markdown(
        f"""
        - 국내 지역 중 **{top_region}**에서 범죄 발생 건수가
          가장 높게 나타났으며, 총 **{top_region_value:,}건**으로 집계되었습니다.
        - 발생 건수가 가장 낮은 지역은 **{low_region}**이며,
          총 **{low_region_value:,}건**으로 집계되었습니다.
        - 상위 5개 지역의 발생 건수는 전체의
          **{top5_ratio:.1f}%**를 차지합니다.
        """
    )

    st.info(
        "해석: 지역별 범죄 발생 건수는 인구 규모, 유동 인구, "
        "지역 특성 등에 영향을 받을 수 있습니다. "
        "따라서 발생 건수만으로 해당 지역의 실제 범죄 위험도를 "
        "단정할 수는 없습니다."
    )

    # 자동 분석 결과 2
    st.divider()
    st.subheader("② 범죄 유형별 분석")

    st.markdown(
        f"""
        - 범죄대분류 중 **{top_category}**의 발생 건수가
          **{top_category_value:,}건**으로 가장 높습니다.
        - 이 유형은 국내 전체 발생 건수의
          **{category_ratio:.1f}%**를 차지합니다.
        - 범죄중분류에서는 **{top_detail}**이
          **{top_detail_value:,}건**으로 가장 높게 나타났습니다.
        """
    )

    # 자동 분석 결과 3
    st.divider()
    st.subheader("③ 지역별 주요 범죄 유형 분석")

    st.markdown(
        f"""
        - 발생 건수가 가장 높았던 **{top_region}**의 주요 범죄 유형은
          **{dominant_category}**입니다.
        - 해당 지역에서 이 범죄 유형은 총
          **{dominant_value:,}건**으로 집계되었습니다.
        """
    )

    # 자동 분석 결과 4
    st.divider()
    st.subheader("④ 종합 분석 및 결론")

    st.success(
        f"""
        이번 통계 분석에서는 국내 전체 범죄 발생 건수가
        {national_total:,}건으로 집계되었습니다.

        지역별로는 {top_region}의 발생 건수가 가장 높았으며,
        범죄 유형별로는 {top_category}가 가장 높은 비중을 보였습니다.

        또한 상위 5개 지역의 발생 건수 비중은 {top5_ratio:.1f}%로,
        지역별 범죄 발생 건수에 차이가 있음을 확인할 수 있었습니다.

        이러한 결과를 통해 범죄 통계는 지역별·유형별로 구분하여
        분석할 필요가 있다는 점을 알 수 있습니다.
        """
    )

    st.caption(
        "※ 본 분석은 제공된 통계의 국내 지역별 발생 건수를 합산한 결과입니다. "
        "인구 대비 발생률이나 시간에 따른 증감 추세를 나타내지는 않습니다."
    )

else:
    st.warning("분석할 범죄 통계 데이터가 없습니다.")
