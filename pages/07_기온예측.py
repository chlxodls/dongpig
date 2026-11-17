
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path
import io

# ---------------------------------
# 1. 페이지 설정
# ---------------------------------

st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")

st.write(
    "과거 기온 데이터를 분석하고 "
    "선형회귀 알고리즘을 이용하여 미래의 평균기온을 예측합니다."
)

st.divider()


# ---------------------------------
# 2. CSV 파일 불러오기
# ---------------------------------

st.subheader("📂 기온 데이터 불러오기")

uploaded_file = st.file_uploader(
    "temperature.csv 파일을 업로드하세요.",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        source_name = uploaded_file.name

    else:
        csv_path = Path(__file__).parent / "temperature.csv"

        if not csv_path.exists():
            st.error(
                "temperature.csv 파일을 프로젝트 폴더에 넣거나 "
                "위에서 업로드해 주세요."
            )
            st.stop()

        file_bytes = csv_path.read_bytes()
        source_name = "temperature.csv"

    # CSV 인코딩 확인
    df = None

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        st.error("CSV 파일의 인코딩을 확인해 주세요.")
        st.stop()

    df.columns = df.columns.str.strip()

    # 필수 열 확인
    required_columns = ["일시", "평균기온(℃)"]

    for col in required_columns:
        if col not in df.columns:
            st.error(f"CSV 파일에 '{col}' 열이 없습니다.")
            st.stop()

    # 날짜 데이터 변환
    df["날짜"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 평균기온 숫자로 변환
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    # 결측값 제거
    df = df.dropna(
        subset=["날짜", "평균기온(℃)"]
    )

    if df.empty:
        st.error("분석할 수 있는 기온 데이터가 없습니다.")
        st.stop()

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 2025년까지만 실제 데이터 사용
    df = df[df["연도"] <= 2025].copy()

    if df.empty:
        st.error("2025년까지의 데이터가 없습니다.")
        st.stop()

    # 같은 연도와 월에 데이터가 여러 개라면 평균 계산
    monthly_df = (
        df.groupby(["연도", "월"], as_index=False)
        ["평균기온(℃)"].mean()
    )

    st.success(
        f"데이터 불러오기 완료! ({source_name})"
    )

except Exception as e:
    st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
    st.stop()


# ---------------------------------
# 3. 데이터 정보
# ---------------------------------

st.subheader("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 데이터 개수",
        f"{len(monthly_df)}개"
    )

with col2:
    st.metric(
        "시작 연도",
        f"{monthly_df['연도'].min()}년"
    )

with col3:
    st.metric(
        "마지막 실제 데이터",
        "2025년"
    )

st.divider()


# ---------------------------------
# 4. 월 및 예측 연도 선택
# ---------------------------------

st.subheader("⚙️ 예측 조건 설정")

col1, col2 = st.columns(2)

month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

with col1:
    selected_month = st.selectbox(
        "분석할 월을 선택하세요.",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    prediction_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=2026,
        max_value=2100,
        value=2026,
        step=1
    )

# 선택한 월 데이터 추출
month_df = monthly_df[
    monthly_df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.warning(
        "선택한 월의 데이터가 2개 미만입니다."
    )
    st.stop()


# ---------------------------------
# 5. 선형회귀 알고리즘 학습
# ---------------------------------

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

model = LinearRegression()

model.fit(X, y)

# 과거 데이터 회귀 예측값
month_df["회귀예측기온"] = model.predict(X)

# 미래 예측
future_X = pd.DataFrame({
    "연도": [int(prediction_year)]
})

predicted_temp = model.predict(future_X)[0]

# 회귀식 정보
slope = model.coef_[0]
intercept = model.intercept_

# 결정계수
r2 = model.score(X, y)


# ---------------------------------
# 6. 예측 결과 출력
# ---------------------------------

st.divider()

st.subheader("🔮 평균기온 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택한 월",
        month_names[selected_month]
    )

with col2:
    st.metric(
        "예측 연도",
        f"{int(prediction_year)}년"
    )

with col3:
    st.metric(
        "예측 평균기온",
        f"{predicted_temp:.2f} ℃"
    )

st.success(
    f"{int(prediction_year)}년 "
    f"{month_names[selected_month]}의 "
    f"예측 평균기온은 {predicted_temp:.2f}℃입니다."
)


# ---------------------------------
# 7. 선형회귀 그래프 시각화
# ---------------------------------

st.divider()

st.subheader("📈 과거 평균기온 및 미래 예측 그래프")

fig = go.Figure()

# 실제 데이터는 2025년까지만 표시
actual_df = month_df[
    month_df["연도"] <= 2025
].copy()

# 실제 평균기온 그래프
fig.add_trace(go.Scatter(
    x=actual_df["연도"],
    y=actual_df["평균기온(℃)"],
    mode="markers+lines",
    name="실제 평균기온",
    marker=dict(size=9),
    line=dict(width=2)
))

# 회귀 직선은 2025년까지만 표시
line_years = np.linspace(
    int(actual_df["연도"].min()),
    2025,
    300
)

line_X = pd.DataFrame({
    "연도": line_years
})

line_y = model.predict(line_X)

fig.add_trace(go.Scatter(
    x=line_years,
    y=line_y,
    mode="lines",
    name="선형회귀 추세선",
    line=dict(
        width=3,
        dash="dash"
    )
))

# 실제 데이터와 회귀 직선 사이의 잔차
residual_x = []
residual_y = []

for _, row in actual_df.iterrows():

    residual_x.extend([
        row["연도"],
        row["연도"],
        None
    ])

    residual_y.extend([
        row["평균기온(℃)"],
        row["회귀예측기온"],
        None
    ])

fig.add_trace(go.Scatter(
    x=residual_x,
    y=residual_y,
    mode="lines",
    name="잔차 (오차)",
    line=dict(
        width=1.5,
        dash="dot"
    )
))

# 미래 예측 지점
fig.add_trace(go.Scatter(
    x=[prediction_year],
    y=[predicted_temp],
    mode="markers+text",
    name="미래 예측기온",
    marker=dict(
        size=16,
        symbol="star"
    ),
    text=[
        f"{predicted_temp:.2f}℃"
    ],
    textposition="top center"
))

# 그래프 디자인
fig.update_layout(
    title=f"{month_names[selected_month]} 평균기온 선형회귀 분석",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    template="plotly_white",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

# 그래프 범위 설정
fig.update_xaxes(
    range=[
        int(actual_df["연도"].min()) - 1,
        int(prediction_year) + 1
    ],
    dtick=1
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------
# 8. 선형회귀 분석 정보
# ---------------------------------

st.divider()

st.subheader("🧮 선형회귀 알고리즘 분석")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "기울기",
        f"{slope:.4f}"
    )

with col2:
    st.metric(
        "절편",
        f"{intercept:.2f}"
    )

with col3:
    st.metric(
        "결정계수 (R²)",
        f"{r2:.4f}"
    )

st.markdown("### 📐 회귀식")

st.latex(
    rf"\hat{{y}} = {slope:.4f}x + ({intercept:.2f})"
)

st.caption(
    "x는 연도이며, ŷ는 선형회귀 알고리즘이 계산한 평균기온입니다."
)


# ---------------------------------
# 9. 선형회귀 알고리즘 쉽게 설명
# ---------------------------------

st.divider()

st.subheader("💡 선형회귀 알고리즘이란?")

st.write("""
선형회귀는 과거의 데이터를 분석하여
미래의 값을 예측하는 머신러닝 알고리즘입니다.

이번 프로그램에서는 과거의 연도와 평균기온을 학습하여
두 데이터 사이의 관계를 직선으로 표현합니다.
""")

st.markdown("#### ① 실제 데이터 학습")

st.write("""
과거 각 연도의 평균기온을 점으로 표시합니다.

점 하나하나가 실제로 관측된 기온 데이터입니다.
""")

st.markdown("#### ② 가장 적합한 직선 찾기")

st.write("""
알고리즘은 실제 데이터와 직선 사이의 오차를 계산합니다.

오차들의 제곱 합이 가장 작아지도록
가장 적합한 직선을 찾습니다.

이 직선을 회귀 직선이라고 합니다.
""")

st.markdown("#### ③ 미래 기온 예측")

st.write("""
완성된 회귀 직선에 사용자가 입력한 미래 연도를 대입합니다.

그러면 해당 연도의 예상 평균기온을 계산할 수 있습니다.
""")

st.markdown("#### ④ 잔차와 결정계수 확인")

st.write("""
- 잔차: 실제 기온과 회귀 직선이 예측한 기온의 차이입니다.
- 결정계수(R²): 회귀 모델이 과거 데이터의 변화를 얼마나 설명하는지 나타냅니다.

R² 값이 1에 가까울수록 과거 데이터에 대한 설명력이 높습니다.
단, 과거의 경향이 미래에도 그대로 유지된다는 뜻은 아닙니다.
""")

st.info(
    "주의: 선형회귀는 과거 기온의 추세만 이용합니다. "
    "기후변화, 강수량, 바람, 이상기후 등의 요소는 반영하지 않으므로 "
    "실제 미래 기온과 차이가 발생할 수 있습니다."
)


# ---------------------------------
# 10. 선택한 월의 과거 데이터 표
# ---------------------------------

st.divider()

st.subheader("📋 과거 평균기온 데이터")

display_df = actual_df[
    ["연도", "평균기온(℃)", "회귀예측기온"]
].copy()

display_df.columns = [
    "연도",
    "실제 평균기온(℃)",
    "회귀 예측기온(℃)"
]

st.dataframe(
    display_df.style.format({
        "실제 평균기온(℃)": "{:.2f}",
        "회귀 예측기온(℃)": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "본 프로그램은 temperature.csv의 "
    "2025년까지의 평균기온 데이터를 활용한 "
    "선형회귀 분석 프로그램입니다."
)
