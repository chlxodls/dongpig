
import streamlit as st
import pandas as pd
import plotly.express as px
import re
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="행정구별 연령 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 행정구별 연령 인구 분석")
st.caption("행정구 · 연도 · 성별에 따른 연령별 인구 분석")

# =====================================
# 2. 상위 폴더 경로 설정
# =====================================
BASE_DIR = Path(__file__).resolve().parent.parent

# 상위 폴더에 있는 CSV 파일 검색
CSV_FILES = sorted(BASE_DIR.glob("*.csv"))

if not CSV_FILES:
    st.error("상위 폴더에서 CSV 파일을 찾을 수 없습니다.")
    st.info("CSV 파일이 pages 폴더의 상위 폴더에 있는지 확인하세요.")
    st.stop()

# CSV 파일이 여러 개일 경우 선택
if len(CSV_FILES) == 1:
    selected_file = CSV_FILES[0]
else:
    selected_name = st.sidebar.selectbox(
        "데이터 파일 선택",
        [f.name for f in CSV_FILES]
    )
    selected_file = BASE_DIR / selected_name

st.success(f"데이터 파일: {selected_file.name}")

# =====================================
# 3. 한글 인코딩 처리
# =====================================
@st.cache_data
def load_csv(file_path, modified_time):
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인할 수 없습니다.")

try:
    df = load_csv(
        str(selected_file),
        selected_file.stat().st_mtime
    )

    df.columns = df.columns.astype(str).str.strip()

except Exception as e:
    st.error(f"CSV 파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

st.success("데이터를 성공적으로 불러왔습니다!")

# =====================================
# 4. 데이터 미리보기
# =====================================
with st.expander("📁 데이터 미리보기"):
    st.dataframe(df.head(10), use_container_width=True)
    st.write("전체 데이터 크기:", df.shape)

# =====================================
# 5. 컬럼 자동 탐색
# =====================================
def find_column(keywords):
    for col in df.columns:
        if any(word in col.lower() for word in keywords):
            return col
    return None

columns = list(df.columns)

district_default = find_column(["행정구", "자치구", "구별", "구명", "district"])
year_default = find_column(["연도", "년도", "year"])
gender_default = find_column(["성별", "gender", "sex"])
age_default = find_column(["나이", "연령", "age"])
population_default = find_column(["인구수", "인구", "population"])

# =====================================
# 6. 데이터 컬럼 설정
# =====================================
st.subheader("⚙️ 데이터 항목 설정")

def column_selector(label, default):
    index = columns.index(default) if default in columns else 0
    return st.selectbox(label, columns, index=index)

c1, c2, c3 = st.columns(3)

with c1:
    district_col = column_selector("행정구 컬럼", district_default)

with c2:
    year_col = column_selector("연도 컬럼", year_default)

with c3:
    gender_col = column_selector("성별 컬럼", gender_default)

c4, c5 = st.columns(2)

with c4:
    age_col = column_selector("나이 컬럼", age_default)

with c5:
    population_col = column_selector("인구수 컬럼", population_default)

# =====================================
# 7. 데이터 전처리
# =====================================
data = df.copy()

for col in [district_col, year_col, gender_col, age_col]:
    data[col] = data[col].astype(str).str.strip()

data[population_col] = pd.to_numeric(
    data[population_col]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("명", "", regex=False)
    .str.strip(),
    errors="coerce"
)

data = data.dropna(subset=[population_col])

# =====================================
# 8. 사이드바 필터
# =====================================
st.sidebar.header("🔍 분석 조건 선택")

districts = sorted(data[district_col].unique().tolist())
years = sorted(data[year_col].unique().tolist())
genders = sorted(data[gender_col].unique().tolist())

selected_district = st.sidebar.selectbox(
    "행정구 선택",
    districts
)

selected_year = st.sidebar.selectbox(
    "연도 선택",
    years
)

selected_gender = st.sidebar.selectbox(
    "성별 선택",
    ["전체"] + genders
)

# =====================================
# 9. 데이터 필터링
# =====================================
filtered = data[
    (data[district_col] == selected_district) &
    (data[year_col] == selected_year)
].copy()

if selected_gender != "전체":
    filtered = filtered[
        filtered[gender_col] == selected_gender
    ]

# =====================================
# 10. 연령 정렬
# =====================================
def age_sort(value):
    numbers = re.findall(r"\d+", str(value))

    if numbers:
        return (0, int(numbers[0]))

    return (1, str(value))

# =====================================
# 11. 인구수 합산
# =====================================
chart_data = (
    filtered.groupby(age_col, as_index=False)[population_col]
    .sum()
)

chart_data["_sort"] = chart_data[age_col].map(age_sort)

chart_data = chart_data.sort_values("_sort")

# =====================================
# 12. 꺾은선 그래프
# =====================================
st.divider()

st.subheader("📈 연령별 인구수 그래프")

st.write(
    f"행정구: {selected_district} | "
    f"연도: {selected_year} | "
    f"성별: {selected_gender}"
)

if not chart_data.empty:

    fig = px.line(
        chart_data,
        x=age_col,
        y=population_col,
        markers=True,
        labels={
            age_col: "나이",
            population_col: "인구수 (명)"
        },
        title="연령별 인구 분포"
    )

    fig.update_traces(
        line=dict(
            color="green",
            width=3
        ),
        marker=dict(
            color="green",
            size=7
        )
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Malgun Gothic, sans-serif",
            color="black"
        ),
        xaxis=dict(
            title="나이",
            showgrid=True,
            gridcolor="#DDDDDD"
        ),
        yaxis=dict(
            title="인구수 (명)",
            dtick=1000,
            rangemode="tozero",
            showgrid=True,
            gridcolor="#BBBBBB",
            gridwidth=1,
            tickformat=","
        ),
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =================================
    # 13. 통계 요약
    # =================================
    st.subheader("📋 인구 통계 요약")

    total_population = chart_data[population_col].sum()

    max_age = chart_data.loc[
        chart_data[population_col].idxmax(),
        age_col
    ]

    max_population = chart_data[population_col].max()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "총 인구수",
        f"{total_population:,.0f}명"
    )

    col2.metric(
        "인구가 가장 많은 연령",
        str(max_age)
    )

    col3.metric(
        "최대 인구수",
        f"{max_population:,.0f}명"
    )

    # =================================
    # 14. 상세 데이터
    # =================================
    with st.expander("📊 상세 데이터 확인"):
        st.dataframe(
            chart_data.drop(columns=["_sort"]),
            use_container_width=True
        )

else:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
