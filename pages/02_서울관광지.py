
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------

st.set_page_config(
    page_title="서울 외국인 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# ----------------------------------
# 2. 관광지 데이터
# ----------------------------------

PLACES = [
    {
        "rank": 1,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9850,
        "category": "쇼핑·먹거리",
        "description": "K-뷰티 매장과 패션 상점, 길거리 음식이 모여 있는 서울 대표 쇼핑 거리입니다.",
        "reason": "화장품 쇼핑과 한국 길거리 음식을 경험하기 좋아요."
    },
    {
        "rank": 2,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "description": "남산 정상 부근에 있는 전망 명소로 서울 도심을 한눈에 볼 수 있습니다.",
        "reason": "서울의 전경과 야경을 감상하기 좋아요."
    },
    {
        "rank": 3,
        "name": "코엑스·별마당도서관",
        "english": "COEX & Starfield Library",
        "lat": 37.5125,
        "lon": 127.0588,
        "category": "쇼핑·문화",
        "description": "대형 쇼핑 공간과 높은 책장이 인상적인 별마당도서관이 있는 곳입니다.",
        "reason": "쇼핑, 전시, 식사를 함께 즐길 수 있어요."
    },
    {
        "rank": 4,
        "name": "강남역 일대",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "쇼핑·도심",
        "description": "상점과 음식점, 카페가 밀집한 서울의 대표적인 번화가입니다.",
        "reason": "현대적인 서울의 거리 분위기를 경험하기 좋아요."
    },
    {
        "rank": 5,
        "name": "홍대거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "공연, 음악, 패션, 개성 있는 카페와 상점으로 유명합니다.",
        "reason": "한국의 대중문화와 거리 공연을 즐기기 좋아요."
    },
    {
        "rank": 6,
        "name": "동대문디자인플라자",
        "english": "DDP",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축·문화",
        "description": "독특한 곡선형 건축물로 유명하며 다양한 전시와 행사가 열립니다.",
        "reason": "미래적인 건축물과 전시를 감상하기 좋아요."
    },
    {
        "rank": 7,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장·음식",
        "description": "빈대떡, 김밥, 만두 등 다양한 한국 음식을 맛볼 수 있는 전통시장입니다.",
        "reason": "한국의 시장 분위기와 전통 먹거리를 경험하기 좋아요."
    },
    {
        "rank": 8,
        "name": "남대문시장",
        "english": "Namdaemun Market",
        "lat": 37.5592,
        "lon": 126.9770,
        "category": "전통시장·쇼핑",
        "description": "의류, 잡화, 기념품과 먹거리를 판매하는 오랜 역사의 전통시장입니다.",
        "reason": "한국의 전통적인 시장 문화를 경험할 수 있어요."
    },
    {
        "rank": 9,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화유산",
        "description": "조선 왕조의 법궁으로 한국 전통 건축과 역사를 살펴볼 수 있습니다.",
        "reason": "한복 체험과 한국의 전통문화를 즐기기 좋아요."
    },
    {
        "rank": 10,
        "name": "서울숲·성수동",
        "english": "Seoul Forest & Seongsu",
        "lat": 37.5445,
        "lon": 127.0374,
        "category": "자연·로컬문화",
        "description": "넓은 도심 공원과 개성 있는 카페, 편집숍이 모여 있는 지역입니다.",
        "reason": "자연과 요즘 서울의 카페 문화를 함께 즐기기 좋아요."
    }
]

# ----------------------------------
# 3. 웹사이트 제목
# ----------------------------------

st.title("🗺️ 외국인이 좋아하는 서울 관광지 TOP 10")

st.markdown("""
서울을 방문하는 외국인 관광객들이 즐겨 찾는
대표 관광지를 지도에서 확인해 보세요.

지도에서 숫자 마커를 클릭하면 관광지 정보를 확인할 수 있습니다.
""")

st.info(
    "※ 관광지 10곳은 서울의 대표 관광지를 바탕으로 선정한 안내용 목록이며, "
    "공식 통합 순위는 아닙니다."
)

# ----------------------------------
# 4. 지도 생성
# ----------------------------------

m = folium.Map(
    location=[37.555, 126.990],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

# 관광지 마커 그룹
marker_cluster = MarkerCluster().add_to(m)

# ----------------------------------
# 5. 관광지 마커 표시
# ----------------------------------

for place in PLACES:

    popup_html = f"""
    <div style="width:230px; font-family:sans-serif;">
        <h3>{place['rank']}. {place['name']}</h3>
        <b>{place['english']}</b>
        <p>{place['description']}</p>
        <hr>
        <b>관광 유형:</b> {place['category']}
    </div>
    """

    folium.Marker(
        location=[
            place["lat"],
            place["lon"]
        ],

        tooltip=f"{place['rank']}. {place['name']}",

        popup=folium.Popup(
            popup_html,
            max_width=280
        ),

        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#1769aa;
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
                {place['rank']}
            </div>
            """,
            icon_size=(32, 32),
            icon_anchor=(16, 16)
        )

    ).add_to(marker_cluster)

# ----------------------------------
# 6. 지도 화면 출력
# ----------------------------------

st.subheader("📍 서울 주요 관광지 지도")

st.caption(
    "숫자 마커를 클릭하면 관광지 이름과 설명을 볼 수 있습니다."
)

st_folium(
    m,
    height=600,
    use_container_width=True,
    returned_objects=[]
)

# ----------------------------------
# 7. 관광지 설명
# ----------------------------------

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

                st.markdown(
                    f"**⭐ 추천 이유**"
                )

                st.write(place["reason"])

                st.caption(
                    f"위도: {place['lat']} / 경도: {place['lon']}"
                )

# ----------------------------------
# 8. 참고 자료
# ----------------------------------

st.divider()

st.header("📚 참고 자료")

st.markdown("""
- [서울 공식 관광정보](https://english.visitseoul.net/)
- [서울 데이터 허브](https://data.seoul.go.kr/)
- [OpenStreetMap 지도](https://www.openstreetmap.org/)
""")

st.caption(
    "본 웹사이트는 OpenStreetMap을 활용하며 "
    "별도의 Google Maps 또는 Kakao Maps API 키가 필요하지 않습니다."
)
