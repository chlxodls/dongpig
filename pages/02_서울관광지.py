
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title="서울 외국인 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 서울 주요 관광지 데이터
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

# 제목
st.title("🗺️ 외국인이 좋아하는 서울 관광지 TOP 10")
st.write(
    "서울을 방문하는 외국인 관광객들이 즐겨 찾는 "
    "대표 관광지를 지도에서 확인해 보세요."
)

st.info(
    "서울의 대표 관광지를 소개하기 위한 안내용 목록입니다. "
    "공식 통합 관광지 순위와는 다릅니다."
)

# 서울 지도 생성
m = folium.Map(
    location=[37.555, 126.990],
    zoom_start=12,
    tiles="CartoDB positron"
)

# 관광지 마커 표시
cluster = MarkerCluster().add_to(m)

for place in PLACES:

    popup_html = f"""
    <div style="width:220px">
        <h4>{place['rank']}. {place['name']}</h4>
        <b>{place['english']}</b>
        <p>{place['description']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{place['rank']}. {place['name']}",
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#1769aa;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                line-height:26px;
                text-align:center;
                font-weight:bold;
                font-size:13px;
            ">{place['rank']}</div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )
    ).add_to(cluster)

# 지도 출력
st.subheader("📍 서울 관광지 지도")

st_folium(
    m,
    width=None,
    height=620,
    use_container_width=True
)

st.divider()

# 관광지 설명
st.subheader("🏙️ 서울 주요 관광지 소개")

for i in range(0, len(PLACES), 2):

    cols = st.columns(2)

    for col, place in zip(cols, PLACES[i:i+2]):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"### {place['rank']}. {place['name']}"
                )

                st.caption(
                    f"{place['english']} · {place['category']}"
                )

                st.write(place["description"])

                st.markdown(
                    f"**추천 이유:** {place['reason']}"
                )

                st.caption(
                    f"위도: {place['lat']} / 경도: {place['lon']}"
                )

st.divider()

st.markdown("### 📚 참고 자료")

st.markdown("""
- [서울 공식 관광정보](https://english.visitseoul.net/)
- [서울시 관광정보](https://data.seoul.go.kr/)
""")

st.caption(
    "※ 관광지 위치와 방문 선호도는 조사 시기와 자료에 따라 달라질 수 있습니다."
)
