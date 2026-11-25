
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="경찰청 범죄 통계 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 경찰청 범죄 통계 분석")
st.caption("Pandas를 활용한 전국 지역별 범죄 데이터 분석")

# --------------------------------
# 1. CSV 파일 자동 불러오기
# --------------------------------

file_name = "경찰청_범죄 발생 지역별 통계_20251231.csv"

# 현재 파일은 pages 폴더에 있으므로
# 부모 폴더에서 CSV 파일 검색
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

# 인코딩 자동 확인
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
    st.error("CSV 파일의 인코딩을 확인할 수 없습니다.")
    st.stop()

st.success("범죄 통계 데이터 자동 로드 완료!")

# --------------------------------
# 2. 기본 데이터 정보
# --------------------------------

st.header("1. 데이터 기본 정보")

col1, col2, col3 = st.columns(3)

col1.metric("데이터 행", f"{df.shape[0]:,}개")
col2.metric("데이터 열", f"{df.shape[1]:,}개")
col3.metric(
    "결측치",
    f"{df.isnull().sum().sum():,}개"
)

with st.expander("원본 데이터 확인"):
    st.dataframe(df, use_container_width=True)

# --------------------------------
# 3. 숫자 데이터 변환
# --------------------------------

area_cols = df.columns[2:]

for col in area_cols:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    ).fillna(0)

df["전체합계"] = df[area_cols].sum(axis=1)

# --------------------------------
# 4. 범죄 유형별 분석
# --------------------------------

st.header("2. 범죄 유형별 발생 현황")

crime_type = (
    df.groupby("범죄대분류")["전체합계"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(crime_type)

# --------------------------------
# 5. 지역별 범죄 발생 분석
# --------------------------------

st.header("3. 지역별 범죄 발생 TOP 10")

region_total = (
    df[area_cols]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(region_total.head(10))

st.dataframe(
    region_total.head(10).rename("발생 건수"),
    use_container_width=True
)

# --------------------------------
# 6. 서울 자치구 분석
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
# 7. 원하는 지역 분석
# --------------------------------

st.header("5. 지역별 상세 분석")

selected_region = st.selectbox(
    "분석할 지역 선택",
    sorted(area_cols)
)

region_data = df[
    ["범죄대분류", "범죄중분류", selected_region]
].sort_values(
    by=selected_region,
    ascending=False
)

st.metric(
    f"{selected_region} 전체 범죄 발생 건수",
    f"{int(df[selected_region].sum()):,}건"
)

st.subheader("범죄 유형별 발생 건수")

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
# 8. 분석 결과
# --------------------------------

st.header("6. 최종 분석 결과")

st.write(
    f"가장 많은 범죄가 발생한 지역은 "
    f"{region_total.index[0]}이며, "
    f"총 {int(region_total.iloc[0]):,}건입니다."
)

st.write(
    f"가장 많이 발생한 범죄 유형은 "
    f"{crime_type.index[0]}이며, "
    f"총 {int(crime_type.iloc[0]):,}건입니다."
)

st.success("모든 데이터 분석이 완료되었습니다!")
