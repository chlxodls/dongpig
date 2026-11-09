import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 비율 분석")
st.write("국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 막대그래프로 확인할 수 있습니다.")

# CSV 파일 경로: app.py와 같은 폴더에 있어야 합니다.
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에 'Country' 열이 없습니다.")

    mbti_columns = [column for column in data.columns if column != "Country"]

    # MBTI 열을 숫자형으로 변환
    for column in mbti_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["Country"])
    data[mbti_columns] = data[mbti_columns].fillna(0)

    return data, mbti_columns

if not DATA_FILE.exists():
    st.error(
        "데이터 파일을 찾을 수 없습니다. "
        "'countriesMBTI_16types.csv' 파일을 app.py와 같은 폴더에 넣어주세요."
    )
    st.stop()

try:
    df, mbti_columns = load_data(DATA_FILE)
except Exception as error:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {error}")
    st.stop()

# 국가 선택
countries = sorted(df["Country"].astype(str).unique().tolist())
selected_country = st.selectbox("국가 선택", countries)

country_data = df.loc[df["Country"].astype(str) == selected_country, mbti_columns]

if country_data.empty:
    st.warning("선택한 국가의 데이터를 찾을 수 없습니다.")
    st.stop()

# 선택 국가의 MBTI 비율을 내림차순으로 정렬
values = country_data.iloc[0].astype(float).sort_values(ascending=False)
types = values.index.tolist()
raw_values = values.values.tolist()

# 데이터가 0~1 사이의 비율이면 퍼센트로 변환
if max(raw_values, default=0) <= 1:
    percentages = [value * 100 for value in raw_values]
    y_axis_title = "비율 (%)"
else:
    percentages = raw_values
    y_axis_title = "비율"

# 1위는 빨간색, 나머지는 파란색 계열에서 점점 밝아지는 그라데이션
blue_gradient = [
    "#1769D2", "#2878D8", "#3987DE", "#4A96E4",
    "#5BA5EA", "#6CB4EF", "#7DC2F3", "#8ED0F6",
    "#9EDBFA", "#AFE4FC", "#BDEBFD", "#C9F0FE",
    "#D3F4FE", "#DDF7FF", "#E7FAFF"
]
bar_colors = ["#E53935"] + blue_gradient[:len(types) - 1]

# 핵심 지표
top_type = types[0]
top_percentage = percentages[0]

metric1, metric2, metric3 = st.columns(3)
metric1.metric("선택한 국가", selected_country)
metric2.metric("가장 높은 유형", top_type)
metric3.metric("1위 비율", f"{top_percentage:.2f}%")

st.subheader(f"{selected_country}의 MBTI 유형별 비율")

fig = go.Figure(
    data=[
        go.Bar(
            x=types,
            y=percentages,
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=[f"{value:.2f}%" for value in percentages],
            textposition="outside",
            hovertemplate="%{x}<br>비율: %{y:.2f}%<extra></extra>"
        )
    ]
)

fig.update_layout(
    xaxis_title="MBTI 유형",
    yaxis_title=y_axis_title,
    template="plotly_white",
    height=560,
    margin=dict(l=40, r=30, t=35, b=45),
    showlegend=False,
    xaxis=dict(categoryorder="array", categoryarray=types),
    yaxis=dict(rangemode="tozero", ticksuffix="%")
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("선택한 국가의 MBTI 비율 표 보기"):
    result_table = pd.DataFrame({
        "MBTI 유형": types,
        "비율": [f"{value:.2f}%" for value in percentages]
    })
    st.dataframe(result_table, use_container_width=True, hide_index=True)

st.caption(
    "참고: 이 그래프는 제공된 CSV 데이터의 비율을 시각화한 것입니다. "
