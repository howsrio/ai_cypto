import pandas as pd

# 함수 정의
def live_cal_book_i_v1(param, gr_bid_level, gr_ask_level, var, mid):
    mid_price = mid

    ratio = param[0]; level = param[1]; interval = param[2]
    _flag = var['_flag']
        
    if _flag: # 첫 번째 라인 건너뛰기
        var['_flag'] = False
        return 0.0

    quant_v_bid = gr_bid_level.quantity ** ratio
    price_v_bid = gr_bid_level.price * quant_v_bid

    quant_v_ask = gr_ask_level.quantity ** ratio
    price_v_ask = gr_ask_level.price * quant_v_ask
        
    askQty = quant_v_ask.values.sum()
    bidPx = price_v_bid.values.sum()
    bidQty = quant_v_bid.values.sum()
    askPx = price_v_ask.values.sum()
    bid_ask_spread = interval
        
    book_price = 0 # 0으로 나누는 것을 방지하기 위해
    if bidQty > 0 and askQty > 0:
        book_price = (((askQty * bidPx) / bidQty) + ((bidQty * askPx) / askQty)) / (bidQty + askQty)

    indicator_value = (book_price - mid_price) / bid_ask_spread
    
    return indicator_value

def cal_mid_price(gr_bid_level, gr_ask_level, group_t):
    level = 5 
    gr_rB = gr_bid_level.head(level)
    gr_rT = gr_ask_level.head(level)
    
    if len(gr_bid_level) > 0 and len(gr_ask_level) > 0:
        bid_top_price = gr_bid_level.iloc[0].price
        bid_top_level_qty = gr_bid_level.iloc[0].quantity
        ask_top_price = gr_ask_level.iloc[0].price
        ask_top_level_qty = gr_ask_level.iloc[0].quantity
        mid_price = (bid_top_price + ask_top_price) * 0.5 
    
        return (mid_price, bid_top_price, ask_top_price, bid_top_level_qty, ask_top_level_qty)
    else:
        return (-1, -1, -2, -1, -1)

def volume_weight_agverage_price(gr_bid_level, gr_ask_level):
    N = 5
    bid_prices = gr_bid_level['price']
    bid_volumes = gr_bid_level['quantity']
    ask_prices = gr_ask_level['price']
    ask_volumes = gr_ask_level['quantity']
    bid_vwap = sum(bid_prices[:N] * bid_volumes[:N]) / sum(bid_volumes[:N])
    ask_vwap = sum(ask_prices[:N] * ask_volumes[:N]) / sum(ask_volumes[:N])
    vwap_spread = ask_vwap - bid_vwap
    return vwap_spread

# 데이터 파일 경로
file_path15 = "orderbook-2024-04-15-bithumb-BTC.csv"
file_path16 = "orderbook-2024-04-16-bithumb-BTC.csv"

# 데이터 프레임 읽기
df15 = pd.read_csv(file_path15)
df16 = pd.read_csv(file_path16)

#데이터 통합
df = pd.concat([df15, df16], axis = 0)

# timestamp 컬럼을 datetime으로 변환
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 결과를 저장할 빈 리스트
results = []

# var 변수 정의
var = {'_flag': True}

# 그룹마다 반복
for gr_o in df.groupby('timestamp'):
    gr_bid_level = gr_o[1][gr_o[1].type == 0]
    gr_ask_level = gr_o[1][gr_o[1].type == 1]
    
    mid_price, bid, ask, bid_qty, ask_qty = cal_mid_price(gr_bid_level, gr_ask_level, gr_o)

    vwap_spread = volume_weight_agverage_price(gr_bid_level,gr_ask_level)
    
    # 'param' 변수 정의 및 할당
    param = [0.2, 5, 1]  # 예시 값
    
    # book imbalance 계산
    book_imbalance = live_cal_book_i_v1(param, gr_bid_level, gr_ask_level, var, mid_price)
    
    # 결과를 리스트에 추가
    results.append([gr_o[0], mid_price, book_imbalance, vwap_spread])
    
    # 결과 프린트
    print(f"Timestamp: {gr_o[0]}, Mid Price: {mid_price}, Book Imbalance: {book_imbalance}, vwap_spread={vwap_spread}")

# 결과를 데이터프레임으로 변환
result_df = pd.DataFrame(results, columns=['timestamp', 'mid_price', 'book_imbalance', 'vwap_spread'])
result_df.to_csv(f"2024-04-15,16-bithumb-BTC-feature.csv", index=False)
    