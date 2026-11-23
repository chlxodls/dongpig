
# --------------------------------
# 2. 데이터 불러오기
# --------------------------------
@st.cache_data
def load_data(file_bytes):

    import io

    # CSV 인코딩 자동 대응
    try:
        data = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(io.BytesIO(file_bytes), encoding="cp949")

    # 필요한 컬럼 추출
    data = data.iloc[:, [2, 3, 4]].copy()

    data.columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    data["꽃잎 길이"] = pd.to_numeric(data["꽃잎 길이"])
    data["꽃잎 너비"] = pd.to_numeric(data["꽃잎 너비"])

    return data


# CSV 파일 업로드
uploaded_file = st.file_uploader(
    "Iris.csv 파일을 업로드하세요.",
    type=["csv"]
)

if uploaded_file is not None:

    df = load_data(uploaded_file.getvalue())

else:

    # 프로젝트 폴더에서 CSV 자동 검색
    base_dir = Path(__file__).resolve().parent

    possible_paths = [
        base_dir / "Iris.csv",
        base_dir.parent / "Iris.csv",
        base_dir.parent.parent / "Iris.csv"
    ]

    csv_path = next(
        (p for p in possible_paths if p.exists()),
        None
    )

    if csv_path is not None:
        df = load_data(csv_path.read_bytes())
    else:
        st.warning("Iris.csv 파일을 업로드해주세요.")
        st.stop()
