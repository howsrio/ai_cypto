import time
import requests
import pandas as pd
import datetime

orderbook_data = pd.DataFrame()
current_date = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')# Get current date
#종료시간 설정
end_date = (datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
            + datetime.timedelta(hours=25)).strftime('%Y-%m-%d %H:%M:%S')



while datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < end_date:
    try:
        # Check if date has changed
        new_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        if new_date != current_date:
            # If date has changed, create a new DataFrame and update current_date
            orderbook_data = pd.DataFrame()
            current_date = new_date

        # Bithumb API에서 주문부 책 데이터 가져오기
        response = requests.get('https://api.bithumb.com/public/orderbook/BTC_KRW/?count=5')
        if response.status_code == 200:
            book = response.json()
            data = book['data']

            # 주문부 책 데이터 출력
            print(data)

            # 입찰 및 요청 DataFrame 생성 및 정렬
            bids = pd.DataFrame(data['bids']).apply(pd.to_numeric)
            bids.sort_values('price', ascending=False, inplace=True)
            bids.reset_index(drop=True, inplace=True)
            bids['type'] = 0  # 입찰을 나타내는 열 추가

            asks = pd.DataFrame(data['asks']).apply(pd.to_numeric)
            asks.sort_values('price', ascending=True, inplace=True)
            asks.reset_index(drop=True, inplace=True)
            asks['type'] = 1  # 요청을 나타내는 열 추가

            # 입찰과 요청을 하나의 DataFrame으로 합치기
            df = pd.concat([bids, asks])

            # timestamp 열 추가 (초단위로 표시)
            df['timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

            # 새로운 데이터를 기존 데이터에 추가
            orderbook_data = pd.concat([orderbook_data, df])

            # 파일명 생성 (날짜 기반)
            csv_file_path = f"orderbook-{current_date}-bithumb-BTC.csv"

            # CSV 파일로 저장
            orderbook_data.to_csv(csv_file_path, index=False, header=['price', 'quantity', 'type', 'timestamp'])

        else:
            print("Failed to fetch data. Status code:", response.status_code)

    except Exception as e:
        print("Error:", e)

    # 5초마다 업데이트
    time.sleep(5)