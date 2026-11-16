# --------------------------------------------------
monthly_df = df.loc[
    df["월"] == selected_month,
    ["연도", "최고기온(℃)", "최저기온(℃)"]
].copy()

monthly_df = monthly_df.dropna(
    subset=["최고기온(℃)", "최저기온(℃)"]
)

monthly_df = monthly_df.sort_values("연도")

if monthly_df.empty:
    st.warning(
        f"{selected_month_name}에 해당하는 기온 데이터가 없습니다."
    )
    st.stop()


# --------------------------------------------------
# 꺾은선 그래프
# --------------------------------------------------
fig = go.Figure()

# 최고기온: 핫핑크
fig.add_trace(
    go.Scatter(
        x=monthly_df["연도"],
        y=monthly_df["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="#FF1493",
            width=3
        ),
        marker=dict(size=6),
        hovertemplate="%{x}년<br>최고기온: %{y}℃<extra></extra>"
    )
)

# 최저기온: 민트색
fig.add_trace(
    go.Scatter(
        x=monthly_df["연도"],
        y=monthly_df["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="#98FFCC",
            width=3
        ),
        marker=dict(size=6),
        hovertemplate="%{x}년<br>최저기온: %{y}℃<extra></extra>"
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
    legend_title="범례",
    hovermode="x unified",
    template="plotly_white",
    font=dict(
        family="Malgun Gothic, AppleGothic, sans-serif",
        size=13
    ),
    height=600,
    margin=dict(l=30, r=30, t=80, b=50)
)

fig.update_xaxes(
    showgrid=True,
    tickformat="d"
)

fig.update_yaxes(
    showgrid=True,
    ticksuffix="℃"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 선택한 월의 데이터 표
# --------------------------------------------------
with st.expander("선택한 월의 원본 분석 데이터 확인"):
    display_df = monthly_df.rename(
        columns={
            "최고기온(℃)": "최고기온 (℃)",
            "최저기온(℃)": "최저기온 (℃)"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 분석 정보
# --------------------------------------------------
st.caption(
    f"선택 월: {selected_month_name} | "
    f"분석 연도: {int(monthly_df['연도'].min())}년 ~ "
    f"{int(monthly_df['연도'].max())}년 | "
    f"데이터 수: {len(monthly_df)}개"
)
