import pyupbit
import datetime
import time

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_target_price_RngThru(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price_RngThru = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price_RngThru

def get_target_price_TurnOvr(ticker):
    tovr = pyupbit.get_ohlcv(ticker,count=10,interval='day') #10일치의 정보 가져오기
    target_price_TurnOvr = max(tovr.iloc[0]['high'],tovr.iloc[1]['high'],tovr.iloc[2]['high'],tovr.iloc[3]['high'],tovr.iloc[4]['high'],tovr.iloc[5]['high'],tovr.iloc[6]['high'],tovr.iloc[7]['high'],tovr.iloc[8]['high'])
    return target_price_TurnOvr

def get_volume_today(ticker):
    vol = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    vol_tday = vol['volume'][1]
    return vol_tday

def get_volume_ystday(ticker):
    vol = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    vol_ystday = vol['volume'][0]
    return vol_ystday 

#r = open('/Users/joohyungkim/Private/3_Python/02_Invest/access_key_AWS.txt','r')
access = 'Aceess'
#r = open('/Users/joohyungkim/Private/3_Python/02_Invest/secret_key_AWS.txt','r')
secret = 'Secret'

#로그인
upbit = pyupbit.Upbit(access, secret)
print("*"*100)
print("Auto-Trading Start!")
print("*"*100)

#markets = pyupbit.get_tickers(fiat="KRW") #KRW의 모든 코인들 확인해서 list 에 넣어줌
Markets_List = ['KRW-XRP','KRW-ETC','KRW-BTC'] #Major 코인을 모니터링
Purchased = [ ] #매수 종목 담기 위한 dummy list

#자동 매수&매도 프로그램
#p = 0
while True:
    try:        
        now = datetime.datetime.now() #현재 시간 업데이트
        start_time = get_start_time("KRW-BTC") #오전 9시
        end_time = start_time + datetime.timedelta(days=1) #다음날 오전 9시
        
        #오늘 09:00:00 < 현재 시간 < 내일 08:59:30
        if start_time < now < end_time - datetime.timedelta(seconds=30):
            k = 0.5
            for j in range(0,len(Markets_List)):
                current_price = get_current_price(Markets_List[j]) #현재 가격 마켓별로 가져오기
                target_price_RngThru = get_target_price_RngThru(Markets_List[j],k)
                target_price_TurnOvr = get_target_price_TurnOvr(Markets_List[j])
                target_price_OverAll = min(target_price_RngThru,target_price_TurnOvr)
                volume_today = get_volume_today(Markets_List[j])
                volume_ystday = get_volume_ystday(Markets_List[j])
                time.sleep(0.2)
                print(Markets_List[j])

                if current_price > min(target_price_RngThru,target_price_TurnOvr): #and volume_today > volume_ystday : #### 5일선 조건 포함하려면 업데이트 해야함. ####
                    krw_bal = get_balance("KRW") #원화 잔고 가져와서
                    if krw_bal > 5000:
                        upbit.buy_market_order(Markets_List[k], krw_bal*0.9995) #매수
                        print("종목:%s || 현재가:%f || 매수가:%f" %(Markets_List[j],current_price,target_price_OverAll))
                        print("어제 거래량:%f || 오늘 거래량:%f" %(volume_ystday,volume_today))
                        print("******Purchased******",Markets_List[j],now)
                        Purchased.append(Markets_List[j])
                        Markets_List.remove(Markets_List[j])
                                                
            # else:
            #     p += 1
            #     print(p)
        #내일 08:59:30 < 현재 시간 < 08:59:45 : 매도
        elif end_time - datetime.timedelta(seconds=30) < now < end_time - datetime.timedelta(seconds=15):
                for k in range(0,len(Purchased)):
                    sell_bal = get_balance(Purchased[k]) # 잔고를 가져와서
                    if sell_bal > 0.0005:
                        upbit.sell_market_order(Purchased[k], sell_bal*0.9995)
                        print("매도 체결 되었습니다.",now)
        
        #내일 08:59:45 < 현재 시간 < 09:00:00 : 리셋
        elif end_time - datetime.timedelta(seconds=15) < now < end_time:
            Markets_List = ['KRW-XRP','KRW-ETC','KRW-BTC']
            Purchased = [ ]

        time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(1)

