
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="대전 1박 2일 여행",
    page_icon="🚄",
    layout="wide"
)

# ==========================================
# 2. 관광지 데이터
# ==========================================

PLACES = [
    {
        "name": "대전역",
        "lat": 36.3325,
        "lon": 127.4347,
        "category": "교통",
        "description": "KTX와 일반열차를 이용할 수 있는 대전의 주요 교통 중심지."
    },
    {
        "name": "성심당 본점",
        "lat": 36.3275,
        "lon": 127.4272,
        "category": "음식·베이커리",
        "description": "튀김소보로와 판타롱 부추빵으로 유명한 대전 대표 베이커리."
    },
    {
        "name": "으능정이 스카이로드",
        "lat": 36.3288,
        "lon": 127.4285,
        "category": "문화·쇼핑",
        "description": "대형 LED 영상 시설이 설치된 대전 원도심의 대표 거리."
    },
    {
        "name": "대전 중앙시장",
        "lat": 36.3295,
        "lon": 127.4345,
        "category": "전통시장",
        "description": "다양한 먹거리와 생활용품을 구경할 수 있는 전통시장."
    },
    {
        "name": "한밭수목원",
        "lat": 36.3683,
        "lon": 127.3885,
        "category": "자연·휴식",
        "description": "도심에서 자연을 즐길 수 있는 넓은 인공 도시 수목원."
    },
    {
        "name": "이응노미술관",
        "lat": 36.3678,
        "lon": 127.3866,
        "category": "예술·문화",
        "description": "한국 현대미술을 대표하는 이응노 화백의 작품을 감상할 수 있는 미술관."
    },
    {
        "name": "대전시립미술관",
        "lat": 36.3665,
        "lon": 127.3852,
        "category": "예술·문화",
        "description": "다양한 현대미술 전시와 문화예술 작품을 감상할 수 있는 공간."
    },
    {
        "name": "엑스포 한빛탑",
        "lat": 36.3755,
        "lon": 127.3840,
        "category": "랜드마크",
        "description": "1993년 대전엑스포를 상징하는 대전의 대표적인 랜드마크."
    },
    {
        "name": "국립중앙과학관",
        "lat": 36.3742,
        "lon": 127.3765,
        "category": "과학·체험",
        "description": "과학기술과 자연과학을 다양한 전시와 체험으로 배울 수 있는 과학관."
    }
]

# ==========================================
# 3. 1박 2일 일정 데이터
# ==========================================

DAY1 = [
    {
        "time": "09:30 ~ 10:00",
        "place": "대전역 도착",
        "transport": "KTX 또는 일반열차",
        "detail": "대전역에 도착한 후 화장실과 편의시설을 이용하고 여행을 시작합니다.",
        "duration": "30분"
    },
    {
        "time": "10:00 ~ 10:20",
        "place": "대전역 → 성심당 본점",
        "transport": "대전 지하철 1호선 대전역 → 중앙로역, 도보 이동",
        "detail": "대전역에서 지하철 1호선을 타고 중앙로역으로 이동합니다. 하차 후 성심당 본점까지 걸어갑니다. 도보 이동도 가능합니다.",
        "duration": "약 20분"
    },
    {
        "time": "10:20 ~ 11:30",
        "place": "성심당 본점",
        "transport": "도보 관광",
        "detail": "대전의 대표 명물인 튀김소보로와 판타롱 부추빵 등을 구입하고 다양한 빵을 구경합니다. 주말에는 대기시간을 넉넉히 잡습니다.",
        "duration": "1시간 10분"
    },
    {
        "time": "11:30 ~ 12:00",
        "place": "으능정이 스카이로드",
        "transport": "도보 약 3~5분",
        "detail": "대전의 대표적인 쇼핑 거리인 은행동을 둘러보고 스카이로드의 대형 LED 화면을 감상합니다.",
        "duration": "30분"
    },
    {
        "time": "12:00 ~ 13:00",
        "place": "점심 식사",
        "transport": "은행동 주변 도보 이동",
        "detail": "은행동 주변 음식점에서 칼국수나 돈가스 등 원하는 메뉴로 점심을 먹습니다.",
        "duration": "1시간"
    },
    {
        "time": "13:00 ~ 14:30",
        "place": "대전 중앙시장",
        "transport": "도보 약 10~15분",
        "detail": "전통시장의 다양한 먹거리와 상점을 구경합니다. 대전의 지역적인 분위기를 경험할 수 있습니다.",
        "duration": "1시간 30분"
    },
    {
        "time": "14:30 ~ 15:00",
        "place": "중앙시장 → 숙소",
        "transport": "택시 또는 대전 지하철 1호선",
        "detail": "정부청사역이나 둔산동 주변 숙소로 이동합니다.",
        "duration": "약 30분"
    },
    {
        "time": "15:00 ~ 16:00",
        "place": "숙소 체크인 및 휴식",
        "transport": "도보",
        "detail": "숙소에 체크인하고 짐을 정리한 뒤 휴식을 취합니다.",
        "duration": "1시간"
    },
    {
        "time": "16:00 ~ 18:00",
        "place": "둔산동 주변 자유시간",
        "transport": "도보 또는 시내버스",
        "detail": "숙소 주변의 카페와 상점을 구경하며 여유로운 시간을 보냅니다.",
        "duration": "2시간"
    },
    {
        "time": "18:00 ~ 19:30",
        "place": "저녁 식사",
        "transport": "도보 이동",
        "detail": "둔산동 주변 식당에서 대전의 지역 음식이나 한식을 즐깁니다.",
        "duration": "1시간 30분"
    }
]

DAY2 = [
    {
        "time": "09:00 ~ 09:30",
        "place": "숙소 출발 → 한밭수목원",
        "transport": "시내버스 또는 택시",
        "detail": "숙소에서 한밭수목원으로 이동합니다. 정부청사역 주변에서는 도보 이동도 가능합니다.",
        "duration": "약 30분"
    },
    {
        "time": "09:30 ~ 11:00",
        "place": "한밭수목원",
        "transport": "도보 관광",
        "detail": "넓은 수목원을 산책하고 다양한 식물과 자연경관을 감상합니다.",
        "duration": "1시간 30분"
    },
    {
        "time": "11:00 ~ 11:40",
        "place": "이응노미술관",
        "transport": "도보 약 5~10분",
        "detail": "이응노 화백의 작품과 한국 현대미술을 감상합니다.",
        "duration": "40분"
    },
    {
        "time": "11:40 ~ 12:30",
        "place": "대전시립미술관",
        "transport": "도보 약 5분",
        "detail": "다양한 현대미술 작품과 기획 전시를 관람합니다.",
        "duration": "50분"
    },
    {
        "time": "12:30 ~ 13:30",
        "place": "점심 식사",
        "transport": "도보 또는 택시",
        "detail": "둔산동이나 엑스포 주변 식당에서 점심을 먹습니다.",
        "duration": "1시간"
    },
    {
        "time": "13:30 ~ 14:30",
        "place": "엑스포과학공원·한빛탑",
        "transport": "도보 또는 시내버스",
        "detail": "한빛탑을 구경하고 엑스포과학공원의 주변 경관과 상징적인 시설을 둘러봅니다.",
        "duration": "1시간"
    },
    {
        "time": "14:30 ~ 15:00",
        "place": "한빛탑 → 국립중앙과학관",
        "transport": "도보 약 15~20분 또는 택시",
        "detail": "과학관 방향으로 이동합니다. 날씨가 좋지 않으면 택시를 이용합니다.",
        "duration": "약 30분"
    },
    {
        "time": "15:00 ~ 16:30",
        "place": "국립중앙과학관",
        "transport": "도보 관광",
        "detail": "과학 전시와 체험 시설을 둘러보고 대전의 과학도시 이미지를 경험합니다.",
        "duration": "1시간 30분"
    },
    {
        "time": "16:30 ~ 17:00",
        "place": "국립중앙과학관 → 대전역",
        "transport": "택시 또는 시내버스",
        "detail": "대전역으로 이동합니다. 택시는 교통 상황에 따라 시간이 달라질 수 있습니다.",
        "duration": "약 30분"
    },
    {
        "time": "17:00 ~ 18:00",
        "place": "대전역 도착 및 귀가",
        "transport": "KTX 또는 일반열차",
        "detail": "열차 출발시간에 맞춰 여유 있게 승강장으로 이동합니다.",
        "duration": "1시간 여유"
    }
]

# ==========================================
# 4. 웹사이트 제목
# ==========================================

st.title("🚄 대전 1박 2일 여행 가이드")

st.markdown("""
대전의 대표 관광지와 먹거리를 둘러보는 1박 2일 여행 코스입니다.

대전의 명물 성심당부터 과학도시의 상징인 엑스포과학공원까지
다양한 매력을 경험해 보세요!
""")

st.info(
    "여행 기준: 대전역 KTX 도착 / 숙소는 정부청사역·둔산동 주변 / "
    "대중교통과 도보 중심"
)

# ==========================================
# 5. 여행 요약
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("여행 기간", "1박 2일")

with col2:
    st.metric("방문 관광지", "7곳")

with col3:
    st.metric("주요 교통수단", "지하철·버스·도보")

# ==========================================
# 6. 대전 지도
# ==========================================

st.divider()

st.header("📍 대전 관광지 지도")

st.write(
    "지도에 표시된 숫자 마커를 클릭하면 관광지 설명을 확인할 수 있습니다."
)

m = folium.Map(
    location=[36.350, 127.405],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

marker_cluster = MarkerCluster().add_to(m)

for i, place in enumerate(PLACES, start=1):

    popup_html = f"""
    <div style="width:230px">
        <h3>{place['name']}</h3>
        <b>{place['category']}</b>
        <p>{place['description']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{i}. {place['name']}",
        popup=folium.Popup(popup_html, max_width=280),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#1769aa;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:32px;
                height:32px;
                line-height:28px;
                text-align:center;
                font-weight:bold;
                font-size:14px;
                box-shadow:0 2px 5px rgba(0,0,0,0.4);
            ">
                {i}
            </div>
            """,
            icon_size=(32, 32),
            icon_anchor=(16, 16)
        )
    ).add_to(marker_cluster)

st_folium(
    m,
    height=580,
    use_container_width=True,
    returned_objects=[]
)

# ==========================================
# 7. 1박 2일 상세 일정
# ==========================================

st.divider()

st.header("🧳 대전 1박 2일 상세 여행 일정")

st.write(
    "각 장소의 방문 시간과 이동 방법, 관광 내용을 확인할 수 있습니다."
)

# DAY 1
with st.expander("🌅 DAY 1 | 대전 원도심과 먹거리 여행", expanded=True):

    st.subheader("첫째 날")

    st.markdown(
        "**대전역 → 성심당 → 으능정이 스카이로드 → 중앙시장 → 숙소**"
    )

    for i, item in enumerate(DAY1, start=1):

        with st.container(border=True):

            st.markdown(f"### {i}. {item['place']}")

            st.markdown(
                f"🕒 **방문 시간:** {item['time']}"
            )

            st.markdown(
                f"🚍 **이동 수단:** {item['transport']}"
            )

            st.write(item["detail"])

            st.caption(
                f"예상 소요시간: {item['duration']}"
            )

# DAY 2
with st.expander("🌳 DAY 2 | 자연·문화·과학 여행", expanded=True):

    st.subheader("둘째 날")

    st.markdown(
        "**한밭수목원 → 이응노미술관 → 대전시립미술관 "
        "→ 한빛탑 → 국립중앙과학관 → 대전역**"
    )

    for i, item in enumerate(DAY2, start=1):

        with st.container(border=True):

            st.markdown(f"### {i}. {item['place']}")

            st.markdown(
                f"🕒 **방문 시간:** {item['time']}"
            )

            st.markdown(
                f"🚍 **이동 수단:** {item['transport']}"
            )

            st.write(item["detail"])

            st.caption(
                f"예상 소요시간: {item['duration']}"
            )

# ==========================================
# 8. 관광지 소개
# ==========================================

st.divider()

st.header("🏙️ 대전 주요 관광지 소개")

for i in range(0, len(PLACES), 2):

    cols = st.columns(2)

    for col, place in zip(cols, PLACES[i:i+2]):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"### {place['name']}"
                )

                st.caption(place["category"])

                st.write(place["description"])

# ==========================================
# 9. 교통 안내
# ==========================================

st.divider()

st.header("🚇 대전 대중교통 이용 안내")

st.markdown("""
### 추천 교통수단

| 교통수단 | 활용 방법 |
|---|---|
| KTX | 서울 등 다른 지역에서 대전역 도착 |
| 대전 지하철 1호선 | 대전역과 원도심, 정부청사역 이동 |
| 시내버스 | 한밭수목원과 과학관 주변 이동 |
| 택시 | 버스 환승이 불편하거나 짐이 많을 때 |
| 도보 | 성심당, 스카이로드, 중앙시장 등 원도심 관광 |

### 여행 준비물

- 교통카드 또는 교통비
- 편한 운동화
- 휴대전화와 충전기
- 개인 소지품
- 숙소 예약 확인서
""")

st.markdown(
    "[대전교통공사](https://www.djtc.kr/)"
)

st.markdown(
    "[코레일 열차 예매](https://www.korail.com/)"
)

st.markdown(
    "[대전 관광 공식 홈페이지](https://www.daejeon.go.kr/tou/index.do)"
)

# ==========================================
# 10. 주의사항 및 참고 자료
# ==========================================

st.divider()

st.header("📌 여행 전 확인사항")

st.warning("""
1. 국립중앙과학관과 미술관은 월요일 휴관 여부를 확인하세요.
2. 한밭수목원은 동원과 서원의 휴원 요일이 다르므로 확인이 필요합니다.
3. 성심당은 주말과 공휴일에 대기시간이 길어질 수 있습니다.
4. 열차 시간에 맞춰 대전역에 미리 도착하세요.
5. 버스와 택시 이동시간은 교통상황에 따라 달라집니다.
""")

st.caption(
    "본 일정은 여행 계획을 위한 예시입니다. "
    "실제 방문 전 시설 운영시간과 대중교통 정보를 확인하세요."
)
