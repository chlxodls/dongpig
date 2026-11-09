
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 비율 분석")
st.write("국가를 선택하면 MBTI 16가지 유형별 비율을 확인할 수 있습니다.")

# 상위 폴더의 CSV 파일 불러오기
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "countriesMBTI_16types.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df.columns = df.columns.str.strip()

    mbti_columns = [
        col for col in df.columns if col != "Country"
    ]

    for col in mbti_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Country"])
    df[mbti_columns] = df[mbti_columns].fillna(0)

    return df, mbti_columns


# 데이터 불러오기
if not DATA_FILE.exists():
    st.error(f"CSV 파일을 찾을 수 없습니다: {DATA_FILE}")
    st.stop()

try:
    df, mbti_columns = load_data()
except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()

# 국가 선택
countries = sorted(df["Country"].astype(str).unique())
selected_country = st.selectbox("국가 선택", countries)

# 선택한 국가 데이터
country_data = df[
    df["Country"].astype(str) == selected_country
]

values = country_data.iloc[0][mbti_columns]
values = values.astype(float).sort_values(ascending=False)

types = values.index.tolist()
percentages = values.tolist()

# 소수 비율을 백분율로 변환
if max(percentages) <= 1:
    percentages = [v * 100 for v in percentages]

# 색상 설정
blue_gradient = [
    "#1769D2", "#2878D8", "#3987DE",
    "#4A96E4", "#5BA5EA", "#6CB4EF",
    "#7DC2F3", "#8ED0F6", "#9EDBFA",
    "#AFE4FC", "#BDEBFD", "#C9F0FE",
    "#D3F4FE", "#DDF7FF", "#E7FAFF"
]

colors = ["#E53935"] + blue_gradient[:len(types)-1]

# 상단 정보
col1, col2, col3 = st.columns(3)

col1.metric("선택 국가", selected_country)
col2.metric("1위 MBTI", types[0])
col3.metric("1위 비율", f"{percentages[0]:.2f}%")

# 그래프
st.subheader(f"{selected_country} MBTI 분포")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=types,
        y=percentages,
        marker_color=colors,
        text=[f"{v:.2f}%" for v in percentages],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}: %{y:.2f}%<extra></extra>"
    )
)

fig.update_layout(
    template="plotly_white",
    height=560,
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    showlegend=False,
    yaxis=dict(
        rangemode="tozero",
        ticksuffix="%"
    )
)

st.plotly_chart(fig, use_container_width=True)

# 상세 표
with st.expander("📊 MBTI 상세 비율 확인"):
    result = pd.DataFrame({
        "순위": range(1, 17),
        "MBTI": types,
        "비율": [f"{v:.2f}%" for v in percentages]
    })

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "본 결과는 제공된 CSV 데이터에 기반한 분석입니다."
)
