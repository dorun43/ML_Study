import schedule
import time
from datetime import datetime

def my_function():
    print("실행됨:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(10)

# 09:00부터 15:00까지 1분마다 실행
for hour in range(9, 20 + 1):  # 9시부터 15시까지 반복
    for minute in range(0, 60):  # 매 1분마다
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(my_function)

# 실행 루프 (계속 실행)
while True:
    schedule.run_pending()
    time.sleep(1)  # CPU 사용률을 줄이기 위해 1초 대기
    print('cheking...')
