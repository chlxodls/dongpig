
import streamlit as st
import pandas as pd
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
# 2. 데이터 불러오기
# --------------------------------
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "Iris.csv"

    # 업로드한 CSV 파일은 CP949 인코딩 사용
    data = pd.read_csv(file_path, encoding="cp949")

    # 실제 CSV의 컬럼 위치를 기준으로 데이터 추출
    data = data.iloc[:, [2, 3, 4]].copy()

    data.columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    data["꽃잎 길이"] = pd.to_numeric(data["꽃잎 길이"])
    data["꽃잎 너비"] = pd.to_numeric(data["꽃잎 너비"])

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.info("Iris.csv 파일이 app.py와 같은 폴더에 있는지 확인하세요.")
    st.stop()

# --------------------------------
# 3. 머신러닝 모델 생성
# --------------------------------
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# --------------------------------
# 4. 데이터 범위 안내
# --------------------------------
st.subheader("📌 입력 가능한 데이터 범위")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "꽃잎 길이",
        f"{df['꽃잎 길이'].min():.1f} ~ {df['꽃잎 길이'].max():.1f} cm"
    )

with col2:
    st.metric(
        "꽃잎 너비",
        f"{df['꽃잎 너비'].min():.1f} ~ {df['꽃잎 너비'].max():.1f} cm"
    )

st.caption("위 범위는 Iris.csv 데이터의 최솟값과 최댓값을 기준으로 합니다.")

st.divider()

# --------------------------------
# 5. 사용자 입력
# --------------------------------
st.subheader("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=float(df["꽃잎 길이"].min()),
        max_value=float(df["꽃잎 길이"].max()),
        value=1.4,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=float(df["꽃잎 너비"].min()),
        max_value=float(df["꽃잎 너비"].max()),
        value=0.2,
        step=0.1,
        format="%.1f"
    )

# --------------------------------
# 6. 품종 예측
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

    if prediction == "Iris-setosa":
        korean_name = "아이리스 세토사 (Setosa)"
    elif prediction == "Iris-versicolor":
        korean_name = "아이리스 버시컬러 (Versicolor)"
    else:
        korean_name = "아이리스 버지니카 (Virginica)"

    st.markdown(
        f"<h2 style='text-align:center;'>{korean_name}</h2>",
        unsafe_allow_html=True
    )

    st.write(f"예측 품종: **{prediction}**")

    st.write("### 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": classes,
        "예측 확률": probabilities
    })

    probability_df["예측 확률"] = (
        probability_df["예측 확률"] * 100
    )

    st.bar_chart(
        probability_df.set_index("품종")
    )

    st.divider()

    # --------------------------------
    # 7. 산점도 그래프
    # --------------------------------
    st.subheader("📊 꽃잎 크기별 품종 분포")

    fig, ax = plt.subplots(figsize=(10, 6))

    # 기존 붓꽃 데이터
    for species in df["품종"].unique():

        species_data = df[df["품종"] == species]

        ax.scatter(
            species_data["꽃잎 길이"],
            species_data["꽃잎 너비"],
            label=species,
            alpha=0.7,
            s=45
        )

    # 사용자가 입력한 위치: 노란색 별
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
        f"노란색 별표(★)가 입력한 위치입니다. "
        f"꽃잎 길이 {petal_length:.1f}cm, "
        f"꽃잎 너비 {petal_width:.1f}cm"
    )

# --------------------------------
# 8. 데이터 미리보기
# --------------------------------
with st.expander("📋 Iris 데이터 확인하기"):

    st.dataframe(df, use_container_width=True)

    st.write("전체 데이터 개수:", len(df))

    st.write("품종별 데이터 개수:")
    st.write(df["품종"].value_counts())
