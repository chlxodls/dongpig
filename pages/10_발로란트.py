
import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote

# -----------------------------------------
# 1. 기본 설정
# -----------------------------------------
st.set_page_config(
    page_title="VALORANT 한국 서버 통계",
    page_icon="🎮",
    layout="wide"
)

API_URL = "https://api.ugilabs.com"
REGION = "kr"

st.title("🎮 VALORANT 한국 서버 통계")
st.caption("실제 경쟁전 경기 기록 기반 분석")
st.divider()

# -----------------------------------------
# 2. 랭크 변환
# -----------------------------------------
rank_names = {
    0: "언랭크",
    3: "아이언 1",
    4: "아이언 2",
    5: "아이언 3",
    6: "브론즈 1",
    7: "브론즈 2",
    8: "브론즈 3",
    9: "실버 1",
    10: "실버 2",
    11: "실버 3",
    12: "골드 1",
    13: "골드 2",
    14: "골드 3",
    15: "플래티넘 1",
    16: "플래티넘 2",
    17: "플래티넘 3",
    18: "다이아몬드 1",
    19: "다이아몬드 2",
    20: "다이아몬드 3",
    21: "초월자 1",
    22: "초월자 2",
    23: "초월자 3",
    24: "불멸 1",
    25: "불멸 2",
    26: "불멸 3",
    27: "레디언트"
}

rank_order = list(rank_names.values())

def get_rank(tier):
    try:
        return rank_names.get(int(tier), "랭크 정보 없음")
    except (TypeError, ValueError):
        return "랭크 정보 없음"


# -----------------------------------------
# 3. API 요청 함수
# -----------------------------------------
def api_get(endpoint, api_key, params=None):

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    response = requests.get(
        API_URL + endpoint,
        headers=headers,
        params=params,
        timeout=25
    )

    try:
        result = response.json()
    except ValueError:
        raise Exception("API 응답을 해석할 수 없습니다.")

    if response.status_code != 200:
        message = result.get(
            "error",
            "알 수 없는 API 오류"
        )
        code = result.get("code", "")

        raise Exception(
            f"API 오류 {response.status_code}: "
            f"{message} ({code})"
        )

    if result.get("status", 200) != 200:
        raise Exception(
            result.get("error", "API 요청 실패")
        )

    return result.get("data", result)


# -----------------------------------------
# 4. Riot ID 입력
# -----------------------------------------
st.subheader("🔎 플레이어 검색")

try:
    saved_key = st.secrets["UGI_API_KEY"]
except Exception:
    saved_key = ""

with st.form("search_form"):

    if saved_key:
        api_key = saved_key
        st.success("Streamlit Secrets에서 API 키를 불러왔습니다.")
    else:
        api_key = st.text_input(
            "ugiAPI Key",
            type="password",
            help="API 키는 채팅에 공유하지 마세요."
        )

    col1, col2 = st.columns(2)

    with col1:
        player_name = st.text_input(
            "Riot ID 이름",
            placeholder="예: PlayerName"
        )

    with col2:
        player_tag = st.text_input(
            "Riot ID 태그",
            placeholder="예: KR1"
        )

    submitted = st.form_submit_button(
        "🔍 실제 통계 가져오기",
        use_container_width=True
    )


# -----------------------------------------
# 5. 실제 데이터 가져오기
# -----------------------------------------
if submitted:

    if not api_key or not player_name or not player_tag:
        st.error("API 키와 Riot ID를 모두 입력해주세요.")
        st.stop()

    try:
        encoded_name = quote(player_name.strip(), safe="")
        encoded_tag = quote(player_tag.strip(), safe="")

        with st.spinner("한국 서버 데이터를 가져오는 중..."):

            # 현재 랭크 조회
            try:
                rank_data = api_get(
                    f"/v1/rank/{REGION}/{encoded_name}/{encoded_tag}",
                    api_key
                )
            except Exception as e:
                rank_data = None
                rank_error = str(e)

            # 최근 경쟁전 5경기 조회
            match_data = api_get(
                f"/v1/matches/{REGION}/{encoded_name}/{encoded_tag}",
                api_key,
                params={
                    "mode": "competitive",
                    "size": 5
                }
            )

        matches = match_data.get("matches", [])

        if not matches:
            st.warning("조회된 경쟁전 기록이 없습니다.")
            st.stop()

        # ---------------------------------
        # 6. 경기 데이터 정리
        # ---------------------------------
        records = []

        for match in matches:

            player = match.get("player", {})

            agent_info = player.get(
                "character_details", {}
            )

            agent_name = agent_info.get(
                "name",
                "알 수 없음"
            )

            team = player.get("team")

            teams = match.get("teams", {})

            result = teams.get(team, {})

            won = result.get("won")

            if won is None:
                continue

            tier = player.get("competitive_tier")

            rank = get_rank(tier)

            map_info = match.get("map_details", {})

            map_name = map_info.get(
                "name",
                "알 수 없음"
            )

            stats = player.get("stats", {})

            records.append({
                "요원": agent_name,
                "랭크": rank,
                "맵": map_name,
                "승리": int(bool(won)),
                "결과": "승리" if won else "패배",
                "킬": stats.get("kills", 0),
                "데스": stats.get("deaths", 0),
                "어시스트": stats.get("assists", 0),
                "시작 시간": match.get("game_start", "")
            })

        if not records:
            st.warning("승패를 확인할 수 있는 경기 데이터가 없습니다.")
            st.stop()

        df = pd.DataFrame(records)

        # ---------------------------------
        # 7. 전체 경기 요약
        # ---------------------------------
        st.success(
            f"{player_name}#{player_tag}의 "
            f"한국 서버 경쟁전 데이터를 불러왔습니다!"
        )

        st.info(
            "분석 범위: 입력한 플레이어의 최근 경쟁전 기록. "
            "한국 서버 전체 플레이어의 통계는 아닙니다."
        )

        st.subheader("📊 경기 요약")

        total_matches = len(df)
        total_wins = int(df["승리"].sum())
        total_losses = total_matches - total_wins

        win_rate = (
            total_wins / total_matches * 100
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("분석 경기", f"{total_matches}회")
        col2.metric("승리", f"{total_wins}회")
        col3.metric("패배", f"{total_losses}회")
        col4.metric("승률", f"{win_rate:.1f}%")

        # ---------------------------------
        # 8. 현재 랭크
        # ---------------------------------
        st.divider()
        st.subheader("🏆 현재 경쟁전 랭크")

        if rank_data:

            current_data = rank_data.get(
                "current_data", {}
            )

            current_tier = current_data.get("currenttier")

            current_rank = get_rank(current_tier)

            if current_rank == "랭크 정보 없음":
                current_rank = current_data.get(
                    "currenttierpatched",
                    "정보 없음"
                )

            col1, col2, col3 = st.columns(3)

            col1.metric("현재 랭크", current_rank)

            col2.metric(
                "RR",
                current_data.get("ranking_in_tier", "정보 없음")
            )

            col3.metric(
                "현재 시즌 승리",
                current_data.get("wins", "정보 없음")
            )

            st.caption(
                f"랭크 기준 시각: "
                f"{current_data.get('as_of', '정보 없음')}"
            )

        else:
            st.warning(
                f"현재 랭크 정보를 조회하지 못했습니다: "
                f"{rank_error}"
            )

        # ---------------------------------
        # 9. 요원별 승률
        # ---------------------------------
        st.divider()
        st.subheader("🎯 요원별 승률")

        agent_stats = (
            df.groupby("요원")
            .agg(
                경기수=("승리", "count"),
                승리=("승리", "sum")
            )
            .reset_index()
        )

        agent_stats["승률"] = (
            agent_stats["승리"] /
            agent_stats["경기수"] * 100
        )

        agent_stats = agent_stats.sort_values(
            "승률",
            ascending=False
        )

        st.bar_chart(
            agent_stats.set_index("요원")[["승률"]]
        )

        st.dataframe(
            agent_stats,
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------
        # 10. 랭크별 승률
        # ---------------------------------
        st.divider()
        st.subheader("🏅 랭크별 승률")

        rank_stats = (
            df.groupby("랭크")
            .agg(
                경기수=("승리", "count"),
                승리=("승리", "sum")
            )
            .reset_index()
        )

        rank_stats["승률"] = (
            rank_stats["승리"] /
            rank_stats["경기수"] * 100
        )

        rank_stats["정렬"] = rank_stats["랭크"].apply(
            lambda x: (
                rank_order.index(x)
                if x in rank_order else 999
            )
        )

        rank_stats = rank_stats.sort_values("정렬")

        st.bar_chart(
            rank_stats.set_index("랭크")[["승률"]]
        )

        st.dataframe(
            rank_stats[
                ["랭크", "경기수", "승리", "승률"]
            ],
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------
        # 11. 랭크별 요원 승률
        # ---------------------------------
        st.divider()
        st.subheader("🎮 랭크별 요원 승률 비교")

        rank_agent_stats = (
            df.groupby(["랭크", "요원"])
            .agg(
                경기수=("승리", "count"),
                승리=("승리", "sum")
            )
            .reset_index()
        )

        rank_agent_stats["승률"] = (
            rank_agent_stats["승리"] /
            rank_agent_stats["경기수"] * 100
        )

        selected_rank = st.selectbox(
            "비교할 랭크 선택",
            rank_agent_stats["랭크"].unique()
        )

        filtered_rank = rank_agent_stats[
            rank_agent_stats["랭크"] == selected_rank
        ].sort_values("승률", ascending=False)

        st.bar_chart(
            filtered_rank.set_index("요원")[["승률"]]
        )

        st.dataframe(
            filtered_rank,
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------
        # 12. 맵별 요원 승률
        # ---------------------------------
        st.divider()
        st.subheader("🗺️ 맵별 요원 승률")

        map_agent_stats = (
            df.groupby(["맵", "요원"])
            .agg(
                경기수=("승리", "count"),
                승리=("승리", "sum")
            )
            .reset_index()
        )

        map_agent_stats["승률"] = (
            map_agent_stats["승리"] /
            map_agent_stats["경기수"] * 100
        )

        selected_map = st.selectbox(
            "맵 선택",
            map_agent_stats["맵"].unique()
        )

        filtered_map = map_agent_stats[
            map_agent_stats["맵"] == selected_map
        ].sort_values("승률", ascending=False)

        st.bar_chart(
            filtered_map.set_index("요원")[["승률"]]
        )

        st.dataframe(
            filtered_map,
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------
        # 13. K/D 분석
        # ---------------------------------
        st.divider()
        st.subheader("⚔️ 요원별 전투 지표")

        combat_stats = (
            df.groupby("요원")
            .agg(
                킬=("킬", "sum"),
                데스=("데스", "sum"),
                어시스트=("어시스트", "sum")
            )
            .reset_index()
        )

        combat_stats["K/D"] = (
            combat_stats["킬"] /
            combat_stats["데스"].replace(0, 1)
        )

        st.dataframe(
            combat_stats,
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------
        # 14. 최근 경기 기록
        # ---------------------------------
        st.divider()
        st.subheader("📋 최근 경쟁전 기록")

        st.dataframe(
            df[
                [
                    "시작 시간",
                    "맵",
                    "요원",
                    "랭크",
                    "결과",
                    "킬",
                    "데스",
                    "어시스트"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        # CSV 다운로드는 선택 사항
        csv = df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "📥 분석 결과 다운로드",
            data=csv,
            file_name="valorant_analysis.csv",
            mime="text/csv"
        )

        st.caption(
            "데이터 출처: ugiAPI / VALORANT 경기 기록"
        )

    except requests.exceptions.Timeout:
        st.error("API 응답 시간이 초과되었습니다. 잠시 후 다시 시도하세요.")

    except requests.exceptions.RequestException:
        st.error("인터넷 연결 또는 API 서버에 문제가 발생했습니다.")

    except Exception as e:
        st.error(f"데이터 처리 오류: {e}")

else:
    st.info(
        "Riot ID와 API 키를 입력하고 검색 버튼을 눌러주세요."
    )

    st.markdown("""
    ### 제공 기능

    - 요원별 승률
    - 랭크별 승률
    - 랭크별 요원 승률
    - 맵별 요원 승률
    - 요원별 K/D 분석
    - 최근 경쟁전 기록
    """)
