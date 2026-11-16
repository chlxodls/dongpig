uploaded_file = st.file_uploader(
    "temperature.csv 파일을 업로드하세요.",
    type=["csv"]
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
else:
    local_file = Path(__file__).parent / "temperature.csv"
    if local_file.exists():
        file_bytes = local_file.read_bytes()
        st.caption("프로젝트 폴더의 temperature.csv 파일을 불러왔습니다.")
    else:
        st.info(
            "분석할 CSV 파일을 업로드해 주세요. "
            "GitHub 프로젝트에 temperature.csv를 함께 올려도 됩니다."
        )
        st.stop()

try:
    df = load_csv(file_bytes)

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        st.error(
            "CSV에 필요한 열이 없습니다: " + ", ".join(missing_columns)
        )
        st.stop()

    df = add_year_and_month(df)

except Exception as error:
    st.error(f"데이터를 불러오는 중 문제가 발생했습니다: {error}")
    st.stop()


# 월 선택
selected_month_name = st.selectbox(
    "분석할 월을 선택하세요.",
    list(MONTH_NAMES.values()),
    index=0
)
selected_month = list(MONTH_NAMES.keys())[
    list(MONTH_NAMES.values()).index(selected_month_name)
]

# 선택한 월의 모든 연도 데이터만 추출
monthly_df = (
    df.loc[df["월"] == selected_month, [
        "연도", "최고기온(℃)", "최저기온(℃)"
    ]]
    .dropna(subset=["최고기온(℃)", "최저기온(℃)"])
    .sort_values("연도")
)

if monthly_df.empty:
    st.warning(f"{selected_month_name}에 해당하는 기온 데이터가 없습니다.")
    st.stop()

# 그래프 작성
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=monthly_df["연도"],
        y=monthly_df["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(color="#FF1493", width=3),
        marker=dict(size=6)
    )
)

fig.add_trace(
    go.Scatter(
        x=monthly_df["연도"],
        y=monthly_df["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(color="#98FFCC", width=3),
        marker=dict(size=6)
    )
)

fig.update_layout(
    title={
        "text": "월별 기온분석",
        "x": 0.5,
        "xanchor": "center"
    },
    xaxis_title="연도",
    yaxis_title="온도 (℃)",
    legend_title="기온 구분",
    hovermode="x unified",
    template="plotly_white",
    font=dict(family="Malgun Gothic, AppleGothic, sans-serif", size=13),
    height=600
)

fig.update_xaxes(
    tickmode="linear",
    dtick=5,
    showgrid=True
)
fig.update_yaxes(showgrid=True)

st.plotly_chart(fig, use_container_width=True)

# 데이터 확인
with st.expander("선택한 월의 분석 데이터 보기"):
    display_df = monthly_df.rename(columns={
        "연도": "연도",
        "최고기온(℃)": "최고기온 (℃)",
        "최저기온(℃)": "최저기온 (℃)"
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.caption(
    f"선택 월: {selected_month_name} · "
    f"분석 연도: {monthly_df['연도'].min()}년~"
    f"{monthly_df['연도'].max()}년 · "
    f"데이터 {len(monthly_df)}개"
)
