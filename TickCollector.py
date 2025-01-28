from pykiwoom.kiwoom import *
import time
import pandas as pd
from datetime import datetime, timedelta

#코스피200 선물 근월물코드를 조회하고 틱데이터를 수집

# 연도 코드 시퀀스
year_code_sequence = [
    "6", "7", "8", "9", "0", "1", "2", "3", "4", "5",
    "A", "B", "C", "D", "E", "F", "G", "H", "J", "K",
    "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W"
]

# 월 코드 매핑 (고정)
month_code_map = {3: "3", 6: "6", 9: "9", 12: "C"}

def get_year_code(year):
    """
    연도에 해당하는 코드 계산
    """
    base_year = 1996
    index = (year - base_year) % len(year_code_sequence)
    return year_code_sequence[index]

def get_next_expiry_month_and_year(current_date):
    """
    현재 날짜 기준으로 다음 만기월과 연도를 계산
    만기월은 3, 6, 9, 12월만 해당
    """
    current_month = current_date.month
    current_year = current_date.year

    # 3, 6, 9, 12 중 다음 만기월 찾기
    for expiry_month in [3, 6, 9, 12]:
        if current_month <= expiry_month:
            return expiry_month, current_year
    # 12월을 넘어가면 다음 해의 3월로 이동
    return 3, current_year + 1

def calculate_kospi200_future_code(target_date=None):
    # 기준 날짜 설정 (기본값은 오늘)
    if target_date is None:
        target_date = datetime.now()
    else:
        target_date = datetime.strptime(target_date, "%Y-%m-%d")

    # 매월 세 번째 목요일 계산
    expiry_month, expiry_year = get_next_expiry_month_and_year(target_date)
    first_day_of_month = datetime(expiry_year, expiry_month, 1)
    weekday_offset = (3 - first_day_of_month.weekday() + 7) % 7
    third_thursday = first_day_of_month + timedelta(days=weekday_offset + 14)

    # 만기일 이후라면 다음 만기월로 이동
    if target_date > third_thursday:
        expiry_month, expiry_year = get_next_expiry_month_and_year(
            third_thursday + timedelta(days=1)
        )

    # 연도 코드와 월 코드 계산
    year_code = get_year_code(expiry_year)
    month_code = month_code_map.get(expiry_month, "0")  # 월 매핑 실패 시 기본값 "0"

    # 최종 코드 반환
    return f"101{year_code}{month_code}000"

# 오늘 날짜 기준 코드 계산
print("오늘 날짜 기준 근월물 코드:", calculate_kospi200_future_code())

# 특정 날짜 테스트
specific_date = "2025-02-18"
print(f"{specific_date} 기준 근월물 코드:", calculate_kospi200_future_code(specific_date))

# 추가 테스트
test_date = "2024-12-01"
print(f"{test_date} 기준 근월물 코드:", calculate_kospi200_future_code(test_date))



# 로그인
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# TR 요청 (연속조회)
dfs = []
df = kiwoom.block_request("opt50028",
                          종목코드=calculate_kospi200_future_code(),
                          시간단위=1,
                          output="선물틱차트조회",
                          next=0)
print(df.head())
dfs.append(df)

#while kiwoom.tr_remained:
for i in range(40):
    for j in range(100):
        df =kiwoom.block_request("opt50028",
                             종목코드=calculate_kospi200_future_code(),
                             시간단위=1,
                             output="선물틱차트조회",
                             next=2)
        dfs.append(df)
        print(i,j)
        time.sleep(1)
    time.sleep(200)
df = pd.concat(dfs)
df.to_excel("선물틱차트_3개월.xlsx")