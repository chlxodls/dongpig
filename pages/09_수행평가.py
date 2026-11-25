
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="VALORANT 한국 서버 통계",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 VALORANT 한국 서버 통계 분석")
st.caption("요원별 · 랭크별 · 맵별 승률 분석 시스템")

st.divider()

# ==========================================
# 2. 기본 설정
# ==========================================
rank_order = [
    "아이언", "브론즈", "실버", "골드",
    "플래티넘", "다이아몬드", "초월자",
    "불멸", "레디언트"
]

rank_alias = {
    "iron": "아이언",
    "bronze": "브론즈",
    "silver": "실버",
    "gold": "골드",
    "platinum": "플래티넘",
    "diamond": "다이아몬드",
    "ascendant": "초월자",
    "immortal": "불멸",
    "radiant": "레디언트"
}

region_alias = {
    "kr": "한국",
    "korea": "한국",
    "한국 서버": "한국",
    "한국": "한국",
    "ap": "아시아 태평양",
    "asia": "아시아 태평양"
}

# ==========================================
# 3. CSV 파일 업로드 및 탐색
# ==========================================
BASE_DIR = Path(__file__).resolve().parent

search_paths = [
    BASE_DIR / "valorant_stats.csv",
    BASE_DIR.parent / "valorant_stats.csv",
    BASE_DIR.parent.parent / "valorant_stats.csv"
]

uploaded_file = st.file_uploader(
    "📂 발로란트 통계 CSV 업로드",
    type=["csv"]
)

st.download_button(
    "📥 CSV 작성 양식 다운로드",
    data=pd.DataFrame(columns=[
        "region", "map", "rank",
        "agent", "role", "wins", "matches"
    ]).to_csv(index=False).encode("utf-8-sig"),
    file_name="valorant_stats_template.csv",
    mime="text/csv"
)

# ==========================================
# 4. 데이터 불러오기
# ==========================================
def read_csv_auto(source):

    for encoding in ["utf-8-sig", "cp949", "latin1"]:

        try:
            if isinstance(source, bytes):
                return pd.read_csv(
                    pd.io.common.BytesIO(source),
                    encoding=encoding
                )
            else:
                return pd.read_csv(
                    source,
                    encoding=encoding
                )

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")


try:

    if uploaded_file is not None:

        df = read_csv_auto(
            uploaded_file.getvalue()
        )

    else:

        csv_path = next(
            (p for p in search_paths if p.exists()),
            None
        )

        if csv_path is None:
            st.info(
                "통계 CSV 파일을 업로드해 주세요."
            )
            st.stop()

        df = read_csv_auto(csv_path)

except Exception as e:

    st.error(f"데이터 불러오기 실패: {e}")
    st.stop()


# ==========================================
# 5. 데이터 검증
# ==========================================
required_columns = [
    "region", "map", "rank",
    "agent", "wins", "matches"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:

    st.error(
        f"CSV에 다음 열이 필요합니다: {missing}"
    )

    st.stop()

if "role" not in df.columns:
    df["role"] = "기타"

# 문자열 정리
for col in ["region", "map", "rank", "agent", "role"]:

    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
    )

# 서버 이름 통일
df["region"] = df["region"].apply(
    lambda x: region_alias.get(x.lower(), x)
)

# 랭크 이름 통일
df["rank"] = df["rank"].apply(
    lambda x: rank_alias.get(x.lower(), x)
)

# 숫자 변환
df["wins"] = pd.to_numeric(
    df["wins"], errors="coerce"
)

df["matches"] = pd.to_numeric(
    df["matches"], errors="coerce"
)

df = df.dropna(
    subset=[
        "region", "map", "rank",
        "agent", "wins", "matches"
    ]
)

df = df[
    (df["wins"] >= 0) &
    (df["matches"] > 0) &
    (df["wins"] <= df["matches"])
].copy()

if df.empty:
    st.error("분석 가능한 데이터가 없습니다.")
    st.stop()

# ==========================================
# 6. 한국 서버 데이터 필터링
# ==========================================
korea_df = df[
    df["region"] == "한국"
].copy()

if korea_df.empty:

    st.warning(
        "한국 서버 데이터가 없습니다. "
        "CSV의 region 열에 KR 또는 한국을 입력해 주세요."
    )

    st.stop()

korea_df["승률"] = (
    korea_df["wins"] /
    korea_df["matches"] * 100
)

st.success(
    f"한국 서버 데이터 확인 완료: "
    f"{len(korea_df):,}개 데이터"
)

# ==========================================
# 7. 전체 통계
# ==========================================
st.subheader("📊 한국 서버 전체 통계")

total_matches = int(korea_df["matches"].sum())
total_wins = int(korea_df["wins"].sum())

overall_rate = (
    total_wins / total_matches * 100
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "총 경기 수",
    f"{total_matches:,}회"
)

col2.metric(
    "총 승리 수",
    f"{total_wins:,}회"
)

col3.metric(
    "가중 평균 승률",
    f"{overall_rate:.2f}%"
)

st.divider()

# ==========================================
# 8. 분석 필터
# ==========================================
st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

available_maps = sorted(
    korea_df["map"].unique()
)

available_ranks = [
    r for r in rank_order
    if r in korea_df["rank"].unique()
]

available_ranks += [
    r for r in korea_df["rank"].unique()
    if r not in rank_order
]

with col1:

    selected_map = st.selectbox(
        "🗺️ 맵 선택",
        available_maps
    )

with col2:

    selected_rank = st.selectbox(
        "🏆 랭크 선택",
        ["전체 랭크"] + available_ranks
    )

with col3:

    selected_role = st.selectbox(
        "🎯 요원 역할 선택",
        ["전체 역할"] +
        sorted(korea_df["role"].unique())
    )

# 필터 적용
filtered_df = korea_df[
    korea_df["map"] == selected_map
].copy()

if selected_rank != "전체 랭크":

    filtered_df = filtered_df[
        filtered_df["rank"] == selected_rank
    ]

if selected_role != "전체 역할":

    filtered_df = filtered_df[
        filtered_df["role"] == selected_role
    ]

if filtered_df.empty:

    st.warning(
        "선택한 조건에 해당하는 데이터가 없습니다."
    )

    st.stop()

# ==========================================
# 9. 맵별 요원 승률 계산
# ==========================================
st.divider()

st.subheader(
    f"🗺️ {selected_map} 맵 요원별 승률"
)

map_agent_stats = (
    filtered_df
    .groupby(
        ["agent", "role"],
        as_index=False
    )
    .agg({
        "wins": "sum",
        "matches": "sum"
    })
)

map_agent_stats["승률"] = (
    map_agent_stats["wins"] /
    map_agent_stats["matches"] * 100
)

map_agent_stats = map_agent_stats.sort_values(
    "승률",
    ascending=False
)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "분석 대상 요원",
        f"{len(map_agent_stats)}명"
    )

with col2:

    st.metric(
        "해당 맵 경기 수",
        f"{int(filtered_df['matches'].sum()):,}회"
    )

# ==========================================
# 10. 맵별 요원 승률 그래프
# ==========================================
st.write("### 📈 요원별 승률 비교")

chart_data = map_agent_stats.set_index(
    "agent"
)[["승률"]]

st.bar_chart(
    chart_data,
    y="승률"
)

# ==========================================
# 11. TOP 5 요원
# ==========================================
st.write("### 🥇 맵별 승률 TOP 5")

top5 = map_agent_stats.head(5).copy()

for i, (_, row) in enumerate(
    top5.iterrows(),
    start=1
):

    col1, col2, col3 = st.columns([1, 3, 2])

    col1.write(f"**{i}위**")
    col2.write(
        f"**{row['agent']}** ({row['role']})"
    )
    col3.write(
        f"**{row['승률']:.2f}%**"
    )

# ==========================================
# 12. 맵별 요원 상세 표
# ==========================================
st.write("### 📋 맵별 상세 통계")

st.dataframe(
    map_agent_stats[
        ["agent", "role", "wins", "matches", "승률"]
    ].rename(columns={
        "agent": "요원",
        "role": "역할",
        "wins": "승리",
        "matches": "경기 수"
    }),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 13. 맵별 전체 요원 비교
# ==========================================
st.divider()

st.subheader("🌍 전체 맵별 요원 승률 비교")

all_map_stats = (
    korea_df
    .groupby(
        ["map", "agent"],
        as_index=False
    )
    .agg({
        "wins": "sum",
        "matches": "sum"
    })
)

all_map_stats["승률"] = (
    all_map_stats["wins"] /
    all_map_stats["matches"] * 100
)

selected_agent = st.selectbox(
    "비교할 요원 선택",
    sorted(korea_df["agent"].unique())
)

agent_map_stats = all_map_stats[
    all_map_stats["agent"] == selected_agent
].sort_values(
    "승률",
    ascending=False
)

st.write(
    f"### {selected_agent} 맵별 승률"
)

st.bar_chart(
    agent_map_stats.set_index("map")[["승률"]]
)

st.dataframe(
    agent_map_stats[
        ["map", "wins", "matches", "승률"]
    ].rename(columns={
        "map": "맵",
        "wins": "승리",
        "matches": "경기 수"
    }),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 14. 랭크별 요원 승률
# ==========================================
st.divider()

st.subheader("🏆 랭크별 요원 승률")

rank_agent_stats = (
    korea_df
    .groupby(
        ["rank", "agent"],
        as_index=False
    )
    .agg({
        "wins": "sum",
        "matches": "sum"
    })
)

rank_agent_stats["승률"] = (
    rank_agent_stats["wins"] /
    rank_agent_stats["matches"] * 100
)

rank_filter = st.selectbox(
    "랭크별 분석 선택",
    available_ranks,
    key="rank_analysis"
)

rank_result = rank_agent_stats[
    rank_agent_stats["rank"] == rank_filter
].sort_values(
    "승률",
    ascending=False
)

st.bar_chart(
    rank_result.set_index("agent")[["승률"]]
)

# ==========================================
# 15. 데이터 미리보기
# ==========================================
with st.expander("📂 한국 서버 원본 데이터 확인"):

    st.dataframe(
        korea_df,
        use_container_width=True
    )

    st.write(
        "데이터 개수:",
        len(korea_df)
    )

    st.write(
        "분석된 맵:",
        available_maps
    )

