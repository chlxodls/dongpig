
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
import io

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="기온 예측 머신러닝 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 머신러닝 예측")
st.write(
    "선형회귀, 다항회귀, 랜덤 포레스트 "
    "알고리즘을 이용하여 미래의 평균기온을 예측합니다."
)

st.divider()


# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================

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
                "직접 업로드해 주세요."
            )
            st.stop()

        file_bytes = csv_path.read_bytes()
        source_name = "temperature.csv"

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
            st.error(f"'{col}' 열을 찾을 수 없습니다.")
            st.stop()

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 기온 숫자 변환
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["날짜", "평균기온(℃)"]
    )

    if df.empty:
        st.error("분석 가능한 데이터가 없습니다.")
        st.stop()

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 실제 데이터는 2025년까지만 사용
    df = df[df["연도"] <= 2025].copy()

    if df.empty:
        st.error("2025년까지의 데이터가 없습니다.")
        st.stop()

    # 월별 데이터 정리
    monthly_df = (
        df.groupby(["연도", "월"], as_index=False)
        ["평균기온(℃)"].mean()
    )

    st.success(
        f"데이터 불러오기 완료! ({source_name})"
    )

except Exception as e:
    st.error(f"데이터 처리 오류: {e}")
    st.stop()


# ==========================================
# 3. 데이터 정보
# ==========================================

st.subheader("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 데이터",
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


# ==========================================
# 4. 월 및 예측 연도 선택
# ==========================================

st.subheader("⚙️ 예측 조건 설정")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

col1, col2 = st.columns(2)

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

# 선택한 월 데이터
month_df = monthly_df[
    monthly_df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.warning(
        "선택한 월의 데이터가 3개 미만입니다."
    )
    st.stop()


# ==========================================
# 5. 머신러닝 알고리즘 학습
# ==========================================

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# ① 선형회귀
linear_model = LinearRegression()
linear_model.fit(X, y)

# ② 다항회귀 (2차)
polynomial_model = make_pipeline(
    PolynomialFeatures(degree=2),
    LinearRegression()
)

polynomial_model.fit(X, y)

# ③ 랜덤 포레스트
forest_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=4,
    min_samples_leaf=2,
    random_state=42
)

forest_model.fit(X, y)


# ==========================================
# 6. 미래 기온 예측
# ==========================================

future_X = pd.DataFrame({
    "연도": [int(prediction_year)]
})

linear_prediction = linear_model.predict(
    future_X
)[0]

polynomial_prediction = polynomial_model.predict(
    future_X
)[0]

forest_prediction = forest_model.predict(
    future_X
)[0]


# ==========================================
# 7. 예측 결과 출력
# ==========================================

st.divider()

st.subheader("🔮 알고리즘별 기온 예측 결과")

st.write(
    f"**{int(prediction_year)}년 "
    f"{month_names[selected_month]} 예상 평균기온**"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선형회귀",
        f"{linear_prediction:.2f} ℃"
    )

with col2:
    st.metric(
        "다항회귀",
        f"{polynomial_prediction:.2f} ℃"
    )

with col3:
    st.metric(
        "랜덤 포레스트",
        f"{forest_prediction:.2f} ℃"
    )

# 예측 결과 비교표
result_df = pd.DataFrame({
    "알고리즘": [
        "선형회귀",
        "다항회귀",
        "랜덤 포레스트"
    ],
    "예측 평균기온(℃)": [
        linear_prediction,
        polynomial_prediction,
        forest_prediction
    ]
})

st.dataframe(
    result_df.style.format({
        "예측 평균기온(℃)": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 8. 그래프 시각화
# ==========================================

st.divider()

st.subheader("📈 세 가지 알고리즘 비교 그래프")

fig = go.Figure()

# 실제 데이터
actual_df = month_df[
    month_df["연도"] <= 2025
].copy()

fig.add_trace(go.Scatter(
    x=actual_df["연도"],
    y=actual_df["평균기온(℃)"],
    mode="markers+lines",
    name="실제 평균기온",
    marker=dict(size=9, color="#318CE7"),
    line=dict(width=2, color="#318CE7")
))

# 회귀 직선 및 곡선은 2025년까지만 표시
line_years = np.linspace(
    int(actual_df["연도"].min()),
    2025,
    300
)

line_X = pd.DataFrame({
    "연도": line_years
})

# 선형회귀 추세선
fig.add_trace(go.Scatter(
    x=line_years,
    y=linear_model.predict(line_X),
    mode="lines",
    name="선형회귀",
    line=dict(
        color="#E45757",
        width=3,
        dash="dash"
    )
))

# 다항회귀 추세선
fig.add_trace(go.Scatter(
    x=line_years,
    y=polynomial_model.predict(line_X),
    mode="lines",
    name="다항회귀",
    line=dict(
        color="#16A36A",
        width=3
    )
))

# 랜덤 포레스트 추세선
fig.add_trace(go.Scatter(
    x=line_years,
    y=forest_model.predict(line_X),
    mode="lines",
    name="랜덤 포레스트",
    line=dict(
        color="#A06CD5",
        width=3
    )
))

# 미래 예측 지점
fig.add_trace(go.Scatter(
    x=[
        prediction_year,
        prediction_year,
        prediction_year
    ],
    y=[
        linear_prediction,
        polynomial_prediction,
        forest_prediction
    ],
    mode="markers+text",
    name="미래 예측값",
    marker=dict(
        size=13,
        symbol="star",
        color=[
            "#E45757",
            "#16A36A",
            "#A06CD5"
        ]
    ),
    text=[
        f"선형 {linear_prediction:.2f}℃",
        f"다항 {polynomial_prediction:.2f}℃",
        f"랜덤 포레스트 {forest_prediction:.2f}℃"
    ],
    textposition="top center"
))

# 그래프 디자인
fig.update_layout(
    title=f"{month_names[selected_month]} 평균기온 머신러닝 분석",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    hovermode="x unified",
    height=650,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

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


# ==========================================
# 9. 알고리즘별 성능 정보
# ==========================================

st.divider()

st.subheader("🧮 머신러닝 알고리즘 분석")

# 학습 데이터 기준 R²
linear_r2 = linear_model.score(X, y)
polynomial_r2 = polynomial_model.score(X, y)
forest_r2 = forest_model.score(X, y)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선형회귀 R²",
        f"{linear_r2:.4f}"
    )

with col2:
    st.metric(
        "다항회귀 R²",
        f"{polynomial_r2:.4f}"
    )

with col3:
    st.metric(
        "랜덤 포레스트 R²",
        f"{forest_r2:.4f}"
    )

st.caption(
    "위 결정계수는 학습 데이터에 대한 값입니다. "
    "미래 예측 정확도를 직접 나타내는 수치는 아닙니다."
)


# ==========================================
# 10. 알고리즘 설명
# ==========================================

st.divider()

st.subheader("💡 머신러닝 알고리즘 쉽게 이해하기")

with st.expander("① 선형회귀 (Linear Regression)"):

    st.write("""
    선형회귀는 과거 데이터의 전체적인 흐름을
    하나의 직선으로 나타내는 알고리즘입니다.

    실제 평균기온과 직선 사이의 오차 제곱 합이
    최소가 되도록 직선을 학습합니다.
    """)

    st.latex(r"\hat{y} = b_0 + b_1x")

    st.write("""
    - x : 연도
    - b₀ : 절편
    - b₁ : 기울기
    - ŷ : 예측 평균기온

    기온이 전체적으로 상승하는지 하락하는지
    확인하기에 적합합니다.
    """)

with st.expander("② 다항회귀 (Polynomial Regression)"):

    st.write("""
    다항회귀는 직선이 아닌 곡선 형태로
    데이터의 변화 패턴을 분석하는 알고리즘입니다.

    이번 프로그램에서는 2차 다항회귀를 사용합니다.
    """)

    st.latex(
        r"\hat{y} = b_0 + b_1x + b_2x^2"
    )

    st.write("""
    - x : 연도
    - x² : 연도의 제곱
    - b₀, b₁, b₂ : 학습을 통해 계산되는 계수

    기온 변화가 일정한 직선 형태가 아니라
    곡선 형태로 나타날 때 활용할 수 있습니다.
    """)

with st.expander("③ 랜덤 포레스트 (Random Forest)"):

    st.write("""
    랜덤 포레스트는 여러 개의 결정 트리를 만들어
    각각의 예측 결과를 결합하는 알고리즘입니다.

    여러 트리의 예측 평균을 계산하여
    최종 기온 예측값을 만들어 냅니다.
    """)

    st.write("""
    작동 과정

    1. 여러 학습용 데이터 표본을 구성합니다.
    2. 각각의 결정 트리를 학습합니다.
    3. 각 트리가 평균기온을 예측합니다.
    4. 여러 트리의 예측값을 평균하여 최종 결과를 계산합니다.

    여러 트리의 결과를 결합하기 때문에
    하나의 결정 트리보다 안정적인 예측을 기대할 수 있습니다.
    """)

st.info(
    "주의: 세 알고리즘 모두 과거 평균기온만 사용합니다. "
    "강수량, 바람, 습도, 기후변화 등은 반영하지 않습니다. "
    "특히 랜덤 포레스트는 학습 데이터 범위 밖의 미래 연도를 "
    "입력하면 실제 추세를 외삽하지 못하고 학습된 기온 범위의 "
    "값을 예측하는 경향이 있습니다."
)


# ==========================================
# 11. 실제 데이터 표
# ==========================================

st.divider()

st.subheader("📋 과거 평균기온 데이터")

display_df = actual_df[
    ["연도", "평균기온(℃)"]
].copy()

display_df.columns = [
    "연도",
    "실제 평균기온(℃)"
]

st.dataframe(
    display_df.style.format({
        "실제 평균기온(℃)": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "본 프로그램은 temperature.csv의 "
    "2007년 이후부터 2025년까지의 실제 평균기온 데이터를 "
    "활용하여 세 가지 머신러닝 알고리즘을 비교합니다."
)
