
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="서울 관광지 1박 2일 여행",
    page_icon="🗺️",
    layout="wide"
)

# =====================================
# 2. 관광지 데이터
# =====================================

PLACES = [
    {
        "rank": 1,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9850,
        "category": "쇼핑·먹거리",
        "description": "K-뷰티 매장과 패션 상점, 길거리 음식이 모여 있는 서울 대표 쇼핑 거리입니다.",
        "reason": "한국의 화장품과 길거리 음식을 경험하기 좋아요."
    },
    {
        "rank": 2,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "description": "남산 정상 부근에 있는 전망 명소입니다.",
        "reason": "서울의 전경과 아름다운 야경을 감상할 수 있어요."
    },
    {
        "rank": 3,
        "name": "코엑스·별마당도서관",
        "english": "COEX & Starfield Library",
        "lat": 37.5125,
        "lon": 127.0588,
        "category": "쇼핑·문화",
        "description": "대형 쇼핑 공간과 높은 책장이 인상적인 별마당도서관이 있습니다.",
        "reason": "쇼핑과 문화생활을 함께 즐기기 좋아요."
    },
    {
        "rank": 4,
        "name": "강남역",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "쇼핑·도심",
        "description": "상점과 음식점, 카페가 밀집한 서울의 번화가입니다.",
        "reason": "현대적인 서울의 모습을 경험할 수 있어요."
    },
    {
        "rank": 5,
        "name": "홍대거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "공연, 음악, 패션, 개성 있는 카페로 유명합니다.",
        "reason": "한국의 대중문화와 거리 공연을 즐기기 좋아요."
    },
    {
        "rank": 6,
        "name": "동대문디자인플라자",
        "english": "DDP",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축·문화",
        "description": "독특한 곡선형 건축물과 다양한 전시가 열리는 문화공간입니다.",
        "reason": "독특한 건축물과 디자인을 감상할 수 있어요."
    },
    {
        "rank": 7,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장·음식",
        "description": "빈대떡, 김밥, 만두 등 다양한 한국 음식을 맛볼 수 있습니다.",
        "reason": "한국의 전통시장과 먹거리를 경험하기 좋아요."
    },
    {
        "rank": 8,
        "name": "남대문시장",
        "english": "Namdaemun Market",
        "lat": 37.5592,
        "lon": 126.9770,
        "category": "전통시장·쇼핑",
        "description": "의류, 잡화, 기념품과 먹거리를 판매하는 전통시장입니다.",
        "reason": "한국의 전통적인 시장 문화를 경험할 수 있어요."
    },
    {
        "rank": 9,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화유산",
        "description": "조선 왕조의 법궁으로 한국의 전통 건축과 역사를 살펴볼 수 있습니다.",
        "reason": "한복 체험과 한국의 전통문화를 즐기기 좋아요."
    },
    {
        "rank": 10,
        "name": "서울숲·성수동",
        "english": "Seoul Forest & Seongsu",
        "lat": 37.5445,
        "lon": 127.0374,
        "category": "자연·로컬문화",
        "description": "넓은 도심 공원과 개성 있는 카페, 편집숍이 모여 있습니다.",
        "reason": "자연과 최신 서울 카페 문화를 함께 즐길 수 있어요."
    }
]

# =====================================
# 3. 1박 2일 여행 일정
# =====================================

DAY1 = [
    {
        "time": "09:00 ~ 09:30",
        "place": "여행 시작 및 숙소 출발",
        "transport": "숙소에서 출발",
        "detail": "숙소가 명동 주변이라고 가정하고 출발합니다. 짐은 숙소에 보관하거나 역의 보관 서비스를 이용합니다.",
        "duration": "30분"
    },
    {
        "time": "09:30 ~ 11:30",
        "place": "경복궁",
        "transport": "지하철 3호선 경복궁역 5번 출구",
        "detail": "궁궐을 둘러보고 근정전과 경회루 등 전통 건축물을 감상합니다. 한복 체험도 추천합니다.",
        "duration": "2시간"
    },
    {
        "time": "11:30 ~ 12:00",
        "place": "경복궁 → 광장시장",
        "transport": "3호선 경복궁역 → 종로3가역, 1호선 환승 → 종로5가역, 도보 이동",
        "detail": "지하철로 이동한 후 종로5가역에서 광장시장까지 걸어갑니다.",
        "duration": "약 30분"
    },
    {
        "time": "12:00 ~ 13:15",
        "place": "광장시장",
        "transport": "도보 관광",
        "detail": "빈대떡, 마약김밥, 만두 등 한국 전통시장 음식을 점심으로 즐깁니다.",
        "duration": "1시간 15분"
    },
    {
        "time": "13:15 ~ 13:40",
        "place": "광장시장 → DDP",
        "transport": "도보 약 15~20분",
        "detail": "종로와 동대문 방향으로 걸어서 이동합니다.",
        "duration": "약 25분"
    },
    {
        "time": "13:40 ~ 15:00",
        "place": "동대문디자인플라자",
        "transport": "도보 관광",
        "detail": "독특한 건축물을 감상하고 전시 공간과 디자인 관련 시설을 둘러봅니다.",
        "duration": "1시간 20분"
    },
    {
        "time": "15:00 ~ 15:20",
        "place": "DDP → 명동",
        "transport": "4호선 동대문역사문화공원역 → 명동역",
        "detail": "지하철 4호선을 이용해 명동으로 이동합니다.",
        "duration": "약 20분"
    },
    {
        "time": "15:20 ~ 17:30",
        "place": "명동",
        "transport": "도보 관광",
        "detail": "K-뷰티 매장과 패션 상점을 구경하고 길거리 음식과 간식을 즐깁니다.",
        "duration": "2시간 10분"
    },
    {
        "time": "17:30 ~ 18:10",
        "place": "명동 → 남산 케이블카 승강장",
        "transport": "도보 약 15~20분 또는 택시",
        "detail": "남산 케이블카 하부 승강장으로 이동합니다. 오르막 구간이 있어 편한 신발을 추천합니다.",
        "duration": "약 40분"
    },
    {
        "time": "18:10 ~ 18:20",
        "place": "남산 케이블카",
        "transport": "남산 케이블카",
        "detail": "케이블카를 이용해 남산 정상 방향으로 올라갑니다. 대기시간은 별도입니다.",
        "duration": "탑승 약 3~5분"
    },
    {
        "time": "18:20 ~ 20:30",
        "place": "N서울타워",
        "transport": "도보 관광",
        "detail": "서울의 야경을 감상하고 전망대와 주변 전망 공간을 둘러봅니다.",
        "duration": "2시간 10분"
    }
]

DAY2 = [
    {
        "time": "09:00 ~ 10:15",
        "place": "남대문시장",
        "transport": "명동 숙소 기준 도보 약 10~15분",
        "detail": "한국 전통시장을 둘러보고 기념품과 간단한 아침 식사를 즐깁니다.",
        "duration": "1시간 15분"
    },
    {
        "time": "10:15 ~ 10:50",
        "place": "남대문시장 → 홍대거리",
        "transport": "4호선 회현역 → 서울역, 공항철도 일반열차 → 홍대입구역",
        "detail": "서울역에서 공항철도로 환승해 홍대입구역까지 이동합니다.",
        "duration": "약 35분"
    },
    {
        "time": "10:50 ~ 13:00",
        "place": "홍대거리",
        "transport": "도보 관광",
        "detail": "홍대의 거리 공연과 패션 상점, 개성 있는 카페를 구경합니다.",
        "duration": "2시간 10분"
    },
    {
        "time": "13:00 ~ 14:00",
        "place": "홍대 점심 식사",
        "transport": "도보 이동",
        "detail": "홍대 주변 음식점에서 한식 또는 다양한 세계 음식을 점심으로 즐깁니다.",
        "duration": "1시간"
    },
    {
        "time": "14:00 ~ 14:45",
        "place": "홍대 → 서울숲·성수동",
        "transport": "2호선 홍대입구역 → 왕십리역, 수인분당선 환승 → 서울숲역",
        "detail": "왕십리역에서 수인분당선으로 환승한 후 서울숲역으로 이동합니다.",
        "duration": "약 45분"
    },
    {
        "time": "14:45 ~ 16:45",
        "place": "서울숲·성수동",
        "transport": "도보 관광",
        "detail": "서울숲을 산책한 뒤 성수동의 카페와 편집숍을 둘러봅니다.",
        "duration": "2시간"
    },
    {
        "time": "16:45 ~ 17:15",
        "place": "서울숲 → 강남역",
        "transport": "택시 또는 버스",
        "detail": "교통 상황에 따라 택시 또는 대중교통을 이용합니다. 택시는 교통 정체에 따라 시간이 달라질 수 있습니다.",
        "duration": "약 30분"
    },
    {
        "time": "17:15 ~ 18:15",
        "place": "강남역",
        "transport": "도보 관광",
        "detail": "강남역 주변의 번화가와 쇼핑 거리를 구경하고 서울의 현대적인 도시 분위기를 경험합니다.",
        "duration": "1시간"
    },
    {
        "time": "18:15 ~ 18:30",
        "place": "강남역 → 코엑스",
        "transport": "2호선 강남역 → 삼성역",
        "detail": "지하철 2호선을 타고 삼성역으로 이동합니다. 하차 후 코엑스 방향으로 이동합니다.",
        "duration": "약 15분"
    },
    {
        "time": "18:30 ~ 20:30",
        "place": "코엑스·별마당도서관",
        "transport": "도보 관광",
        "detail": "별마당도서관을 구경하고 코엑스 쇼핑몰에서 저녁 식사와 쇼핑을 즐기며 여행을 마무리합니다.",
        "duration": "2시간"
    }
]

# =====================================
# 4. 제목 및 소개
# =====================================

st.title("🗺️ 서울 외국인 인기 관광지 TOP 10")

st.markdown("""
서울을 방문하는 외국인 관광객을 위한 관광 안내 웹사이트입니다.

서울의 주요 관광지 10곳과 1박 2일 여행 일정을 한눈에 확인해 보세요.
""")

st.info(
    "관광지 10곳은 대표 관광지를 참고한 안내용 선정이며, "
    "공식 통합 순위는 아닙니다."
)

# =====================================
# 5. 서울 지도
# =====================================

st.header("📍 서울 관광지 위치")

m = folium.Map(
    location=[37.555, 126.990],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

marker_cluster = MarkerCluster().add_to(m)

for place in PLACES:

    popup_html = f"""
    <div style="width:230px">
        <h3>{place['rank']}. {place['name']}</h3>
        <b>{place['english']}</b>
        <p>{place['description']}</p>
        <hr>
        <b>관광 유형:</b> {place['category']}
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{place['rank']}. {place['name']}",
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
            ">{place['rank']}</div>
            """,
            icon_size=(32, 32),
            icon_anchor=(16, 16)
        )
    ).add_to(marker_cluster)

st_folium(
    m,
    height=600,
    use_container_width=True,
    returned_objects=[]
)

# =====================================
# 6. 1박 2일 여행 일정
# =====================================

st.divider()

st.header("🧳 서울 1박 2일 여행 일정")

st.write(
    "총 10곳의 관광지를 효율적으로 방문할 수 있도록 "
    "이동시간과 관광시간을 고려해 구성했습니다."
)

st.warning(
    "숙소는 명동 주변에 있다고 가정했습니다. "
    "교통 소요시간은 예상치이며 실제 운행시간과 교통상황에 따라 달라집니다."
)

# DAY 1
with st.expander("🌅 DAY 1 - 역사, 전통시장, 서울 야경", expanded=True):

    st.subheader("첫째 날 여행 코스")

    st.markdown("""
    **경복궁 → 광장시장 → DDP → 명동 → N서울타워**
    """)

    for i, item in enumerate(DAY1, start=1):

        with st.container(border=True):

            st.markdown(
                f"### {i}. {item['place']}"
            )

            st.markdown(
                f"🕒 **시간:** {item['time']}"
            )

            st.markdown(
                f"🚇 **교통수단:** {item['transport']}"
            )

            st.write(item["detail"])

            st.caption(
                f"예상 소요시간: {item['duration']}"
            )

# DAY 2
with st.expander("🌇 DAY 2 - 쇼핑, K-문화, 현대 서울", expanded=True):

    st.subheader("둘째 날 여행 코스")

    st.markdown("""
    **남대문시장 → 홍대 → 서울숲·성수동 → 강남역 → 코엑스**
    """)

    for i, item in enumerate(DAY2, start=1):

        with st.container(border=True):

            st.markdown(
                f"### {i}. {item['place']}"
            )

            st.markdown(
                f"🕒 **시간:** {item['time']}"
            )

            st.markdown(
                f"🚇 **교통수단:** {item['transport']}"
            )

            st.write(item["detail"])

            st.caption(
                f"예상 소요시간: {item['duration']}"
            )

# =====================================
# 7. 관광지 소개
# =====================================

st.divider()

st.header("🏙️ 서울 주요 관광지 TOP 10 소개")

for i in range(0, len(PLACES), 2):

    cols = st.columns(2)

    for col, place in zip(cols, PLACES[i:i+2]):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"### {place['rank']}. {place['name']}"
                )

                st.caption(
                    f"{place['english']} | {place['category']}"
                )

                st.write(place["description"])

                st.markdown("**⭐ 추천 이유**")

                st.write(place["reason"])

# =====================================
# 8. 교통 이용 안내
# =====================================

st.divider()

st.header("🚇 서울 대중교통 이용 안내")

st.markdown("""
### 교통카드 이용 방법

1. 편의점이나 지하철역에서 T-money 교통카드를 구매합니다.
2. 교통카드에 사용할 금액을 충전합니다.
3. 지하철 개찰구에서 카드를 태그합니다.
4. 버스에서는 승차할 때와 하차할 때 모두 태그합니다.

### 추천 교통수단

| 교통수단 | 이용 목적 |
|---|---|
| 지하철 | 서울의 주요 관광지 이동 |
| 시내버스 | 지하철역에서 먼 관광지 이동 |
| 택시 | 짧은 거리 또는 편리한 이동 |
| 남산 케이블카 | N서울타워 방문 |

""")

st.markdown(
    "[서울시 공식 대중교통 안내](https://english.seoul.go.kr/service/movement/public-transportation/)"
)

st.markdown(
    "[서울 관광 공식 홈페이지](https://english.visitseoul.net/)"
)

st.caption(
    "※ 본 여행 일정은 관광 안내를 위한 예시입니다. "
    "궁궐 휴관일, 시설 운영시간, 대중교통 운행정보는 방문 전에 확인하세요."
)
