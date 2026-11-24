
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# --------------------------------
# 1. 페이지 기본 설정
# --------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측 프로그램",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 붓꽃의 품종을 예측합니다.")
st.divider()


# --------------------------------
# 2. CSV 파일 자동 탐색
# --------------------------------
BASE_DIR = Path(__file__).resolve().parent

search_paths = [
    BASE_DIR / "Iris.csv",
    BASE_DIR.parent / "Iris.csv",
    BASE_DIR.parent.parent / "Iris.csv"
]

CSV_PATH = None

for path in search_paths:
    if path.exists():
        CSV_PATH = path
        break

if CSV_PATH is None:
    st.error("Iris.csv 파일을 찾을 수 없습니다.")
    st.write("검색한 위치:")
    for path in search_paths:
        st.write(str(path))
    st.stop()


# --------------------------------
# 3. CSV 데이터 불러오기
# --------------------------------
@st.cache_data
def load_data(file_path):

    encodings = ["utf-8-sig", "cp949", "latin1"]

    data = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 인코딩을 확인할 수 없습니다.")

    # 열 개수 확인
    if len(data.columns) < 5:
        raise ValueError(
            "CSV 파일에 필요한 데이터 열이 부족합니다."
        )

    # 실제 CSV의 3, 4, 5번째 열 사용
    data = data.iloc[:, [2, 3, 4]].copy()

    # 열 이름 통일
    data.columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    # 숫자 데이터 변환
    data["꽃잎 길이"] = pd.to_numeric(
        data["꽃잎 길이"],
        errors="coerce"
    )

    data["꽃잎 너비"] = pd.to_numeric(
        data["꽃잎 너비"],
        errors="coerce"
    )

    # 품종 데이터 문자열 정리
    data["품종"] = data["품종"].astype(str).str.strip()

    # 결측값 제거
    data = data.dropna()

    data = data[
        (data["품종"] != "") &
        (data["품종"].str.lower() != "nan")
    ]

    if len(data) == 0:
        raise ValueError("학습할 수 있는 데이터가 없습니다.")

    return data


try:
    df = load_data(str(CSV_PATH))
    st.success("🌸 Iris.csv 데이터를 성공적으로 불러왔습니다!")

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# --------------------------------
# 4. 머신러닝 모델 생성
# --------------------------------
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

st.subheader("📌 학습 데이터 정보")

col1, col2, col3 = st.columns(3)

col1.metric("전체 데이터", f"{len(df)}개")
col2.metric("붓꽃 품종 수", f"{df['품종'].nunique()}종")
col3.metric("예측 모델", "Random Forest")


# --------------------------------
# 5. 데이터 범위 안내
# --------------------------------
st.subheader("📌 입력 가능한 데이터 범위")

min_length = float(df["꽃잎 길이"].min())
max_length = float(df["꽃잎 길이"].max())

min_width = float(df["꽃잎 너비"].min())
max_width = float(df["꽃잎 너비"].max())

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "꽃잎 길이",
        f"{min_length:.1f} ~ {max_length:.1f} cm"
    )

with col2:
    st.metric(
        "꽃잎 너비",
        f"{min_width:.1f} ~ {max_width:.1f} cm"
    )

st.caption(
    "입력 범위는 Iris.csv 데이터의 최솟값과 최댓값을 기준으로 합니다."
)

st.divider()


# --------------------------------
# 6. 사용자 입력
# --------------------------------
st.subheader("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

default_length = min(max(1.4, min_length), max_length)
default_width = min(max(0.2, min_width), max_width)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=min_length,
        max_value=max_length,
        value=default_length,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=min_width,
        max_value=max_width,
        value=default_width,
        step=0.1,
        format="%.1f"
    )


# --------------------------------
# 7. 품종 예측
# --------------------------------
if st.button("🌸 품종 예측하기", use_container_width=True):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_

    st.success("품종 예측이 완료되었습니다!")

    st.subheader("🔎 예측 결과")

    # 품종 이름 한글 표시
    name = str(prediction).lower()

    if "setosa" in name:
        korean_name = "아이리스 세토사 (Setosa)"

    elif "versicolor" in name:
        korean_name = "아이리스 버시컬러 (Versicolor)"

    elif "virginica" in name:
        korean_name = "아이리스 버지니카 (Virginica)"

    else:
        korean_name = str(prediction)

    st.markdown(
        f"<h2 style='text-align:center;'>{korean_name}</h2>",
        unsafe_allow_html=True
    )

    st.write(f"예측 품종: **{prediction}**")

    # --------------------------------
    # 8. 품종별 예측 확률
    # --------------------------------
    st.write("### 📊 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": classes,
        "예측 확률": probabilities * 100
    })

    st.bar_chart(
        probability_df.set_index("품종"),
        y="예측 확률"
    )

    st.divider()

    # --------------------------------
    # 9. 산점도 그래프
    # --------------------------------
    st.subheader("📊 꽃잎 크기별 품종 분포")

    fig, ax = plt.subplots(figsize=(10, 6))

    for species in df["품종"].unique():

        species_data = df[
            df["품종"] == species
        ]

        ax.scatter(
            species_data["꽃잎 길이"],
            species_data["꽃잎 너비"],
            label=species,
            alpha=0.7,
            s=45
        )

    # 사용자 입력 위치
    ax.scatter(
        petal_length,
        petal_width,
        color="yellow",
        edgecolors="black",
        marker="*",
        s=350,
        label="사용자 입력 위치",
        zorder=10
    )

    ax.set_xlabel("Petal Length (cm)", fontsize=12)
    ax.set_ylabel("Petal Width (cm)", fontsize=12)

    ax.set_title(
        "Iris Petal Length vs Petal Width",
        fontsize=15
    )

    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)

    plt.close(fig)

    st.info(
        f"노란색 별표(★)가 입력한 위치입니다.\n\n"
        f"꽃잎 길이: {petal_length:.1f}cm\n\n"
        f"꽃잎 너비: {petal_width:.1f}cm"
    )


# --------------------------------
# 10. 데이터 미리보기
# --------------------------------
with st.expander("📋 Iris 데이터 확인하기"):

    st.dataframe(
        df,
        use_container_width=True
    )

    st.write("전체 데이터 개수:", len(df))

    st.write("품종별 데이터 개수:")

    st.write(
        df["품종"].value_counts()
    )
