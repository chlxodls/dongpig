
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="전국 범죄 통계 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 경찰청 범죄 통계 분석")
st.write("판다스를 활용한 전국 지역별 범죄 데이터 분석")

# --------------------------------
# 1. CSV 파일 자동 탐색
# --------------------------------

file_name = "경찰청_범죄 발생 지역별 통계_20251231.csv"

current_dir = Path(__file__).parent
project_dir = current_dir.parent

possible_paths = [
    current_dir / file_name,
    project_dir / file_name,
    Path.cwd() / file_name
]

csv_path = None

for path in possible_paths:
    if path.exists():
        csv_path = path
        break

# --------------------------------
# 2. CSV 파일 업로드 또는 자동 로드
# --------------------------------

uploaded_file = st.file_uploader(
    "CSV 파일을 업로드하세요.",
    type=["csv"]
)

df = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(
            uploaded_file,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(
            uploaded_file,
            encoding="utf-8-sig"
        )

elif csv_path is not None:

    encodings = ["cp949", "utf-8-sig", "euc-kr"]

    for encoding in encodings:
        try:
            df = pd.read_csv(
                csv_path,
                encoding=encoding
            )
            st.success(
                f"CSV 파일 자동 로드 성공: {csv_path.name}"
            )
            break

        except UnicodeDecodeError:
            continue

if df is None:
    st.warning("CSV 파일을 찾지 못했습니다.")

    st.info(
        "프로젝트 최상위 폴더에 CSV 파일을 넣거나 "
        "위의 업로드 버튼으로 파일을 올려주세요."
    )

    st.stop()

# --------------------------------
# 3. 데이터 기본 정보
# --------------------------------

st.header("1. 데이터 기본 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("데이터 행 개수", f"{len(df):,}개")

with col2:
    st.metric("데이터 열 개수", f"{len(df.columns):,}개")

with col3:
    st.metric(
        "결측치 개수",
        f"{df.isnull().sum().sum():,}개"
    )

with st.expander("원본 데이터 확인"):
    st.dataframe(df, use_container_width=True)

# --------------------------------
# 4. 숫자 데이터 처리
# --------------------------------

area_cols = df.columns[2:]

for col in area_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

df["전체합계"] = df[area_cols].sum(axis=1)

# --------------------------------
# 5. 범죄 유형별 분석
# --------------------------------

st.header("2. 범죄 유형별 발생 현황")

crime_type = (
    df.groupby("범죄대분류")["전체합계"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(crime_type)

st.dataframe(
    crime_type.reset_index().rename(
        columns={
            "범죄대분류": "범죄 유형",
            "전체합계": "발생 건수"
        }
    ),
    use_container_width=True
)

# --------------------------------
# 6. 지역별 분석
# --------------------------------

st.header("3. 지역별 범죄 발생 TOP 10")

region_total = (
    df[area_cols]
    .sum()
    .sort_values(ascending=False)
)

top10 = region_total.head(10)

st.bar_chart(top10)

st.dataframe(
    top10.reset_index().rename(
        columns={
            "index": "지역",
            0: "범죄 발생 건수"
        }
    ),
    use_container_width=True
)

# --------------------------------
# 7. 서울 지역 분석
# --------------------------------

st.header("4. 서울 자치구별 범죄 발생 현황")

seoul_cols = [
    col for col in area_cols
    if col.startswith("서울 ")
]

seoul_total = (
    df[seoul_cols]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(seoul_total)

# --------------------------------
# 8. 특정 지역 검색
# --------------------------------

st.header("5. 원하는 지역 분석")

selected_region = st.selectbox(
    "분석할 지역을 선택하세요.",
    sorted(area_cols)
)

region_data = (
    df[["범죄대분류", "범죄중분류", selected_region]]
    .sort_values(
        by=selected_region,
        ascending=False
    )
)

st.subheader(f"📍 {selected_region} 범죄 현황")

st.metric(
    "총 범죄 발생 건수",
    f"{int(df[selected_region].sum()):,}건"
)

st.bar_chart(
    region_data.set_index("범죄중분류")[
        selected_region
    ].head(15)
)

st.dataframe(
    region_data,
    use_container_width=True
)

# --------------------------------
# 9. 최종 분석
# --------------------------------

st.header("6. 분석 결과 요약")

st.write(
    f"가장 많은 범죄가 발생한 지역은 "
    f"{region_total.index[0]}이며, "
    f"발생 건수는 {int(region_total.iloc[0]):,}건입니다."
)

st.write(
    f"가장 높은 범죄 유형은 "
    f"{crime_type.index[0]}이며, "
    f"발생 건수는 {int(crime_type.iloc[0]):,}건입니다."
)

st.success("범죄 통계 분석이 완료되었습니다!")
