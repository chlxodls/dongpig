import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 불러오기
df = pd.read_csv(
    "경찰청_범죄 발생 지역별 통계_20251231.csv",
    encoding="cp949"
)

# 지역 컬럼 추출
area_cols = df.columns[2:]

# 범죄별 전체 합계
df["전체합계"] = df[area_cols].sum(axis=1)

# 범죄 유형별 분석
crime_type = df.groupby(
    "범죄대분류"
)["전체합계"].sum().sort_values(
    ascending=False
)

print("범죄 유형별 발생 건수")
print(crime_type)

# 지역별 분석
region_total = df[area_cols].sum().sort_values(
    ascending=False
)

print("지역별 범죄 발생 TOP 10")
print(region_total.head(10))

# 서울 지역 분석
seoul_cols = [
    col for col in area_cols
    if col.startswith("서울 ")
]

seoul_total = df[seoul_cols].sum().sort_values(
    ascending=False
)

print("서울 지역 범죄 발생 TOP 10")
print(seoul_total.head(10))

# 그래프
crime_type.head(10).plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title("Crime Statistics by Type")
plt.xlabel("Crime Type")
plt.ylabel("Number of Crimes")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
