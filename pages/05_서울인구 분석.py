
# =====================================
# 9. 데이터 필터링 및 오류 진단
# =====================================

st.subheader("🔎 데이터 필터링 확인")

# 공백 및 문자열 정리
for col in [district_col, year_col, gender_col]:
    data[col] = data[col].astype(str).str.strip()

# 조건별 데이터 개수 확인
district_data = data[
    data[district_col] == selected_district
]

year_data = district_data[
    district_data[year_col] == selected_year
]

gender_data = year_data.copy()

if selected_gender != "전체":
    gender_data = gender_data[
        gender_data[gender_col] == selected_gender
    ]

# 진단 결과 출력
d1, d2, d3, d4 = st.columns(4)

d1.metric("전체 데이터", f"{len(data):,}건")
d2.metric("행정구 일치", f"{len(district_data):,}건")
d3.metric("연도 일치", f"{len(year_data):,}건")
d4.metric("최종 데이터", f"{len(gender_data):,}건")

# 필터 결과 확인
if len(district_data) == 0:
    st.error("선택한 행정구 데이터가 없습니다.")

elif len(year_data) == 0:
    st.error("선택한 연도에 해당하는 데이터가 없습니다.")

elif len(gender_data) == 0:
    st.error("선택한 성별에 해당하는 데이터가 없습니다.")

else:
    st.success("모든 필터 조건에 해당하는 데이터를 찾았습니다!")

filtered = gender_data.copy()

# 실제 데이터 확인
with st.expander("선택된 데이터 확인"):
    st.dataframe(filtered, use_container_width=True)

# =====================================
# 오류 확인 기능
# =====================================

try:
    st.write("데이터 처리 상태:", "정상")

except Exception as e:
    st.error("프로그램 실행 중 오류가 발생했습니다.")
    st.exception(e)
