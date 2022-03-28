import pyupbit
import datetime
import time

def get_start_time(ticker):
    #check opening time
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_current_price(ticker):
    #check current price
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_balance(ticker):
    #check balance
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_target_price_RngThru(ticker, k):
    #target price when price is above range*k
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price_RngThru = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price_RngThru

def get_target_price_TurnOvr(ticker):
    tovr = pyupbit.get_ohlcv(ticker,count=10,interval='day') #information within 10days
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

# r = open('/Users/joohyungkim/Private/3_Python/02_Invest/access_key.txt','r')
# access = r.readline()
# r = open('/Users/joohyungkim/Private/3_Python/02_Invest/secret_key.txt','r')
# secret = r.readline()

access = ''
secret = ''

#로그인
upbit = pyupbit.Upbit(access, secret)
print("*"*100)
print("Auto-Trading Start!")
print("*"*100)

#markets = pyupbit.get_tickers(fiat="KRW") #check all markets
Markets_List = ['KRW-XRP','KRW-ETC','KRW-BTC'] #Major coins
Purchased = [ ] #Dummy list for purchased coins

#Automated trading
#p = 0
while True:
    try:        
        now = datetime.datetime.now() #Update current time
        start_time = get_start_time("KRW-BTC") #09:00
        end_time = start_time + datetime.timedelta(days=1) #09:00 1day later
        
        #today 09:00:00 < current time < tomorrow 08:59:30
        if start_time < now < end_time - datetime.timedelta(seconds=30):
            k = 0.5
            for j in range(0,len(Markets_List)):
                current_price = get_current_price(Markets_List[j])
                target_price_RngThru = get_target_price_RngThru(Markets_List[j],k)
                target_price_TurnOvr = get_target_price_TurnOvr(Markets_List[j])
                target_price_OverAll = min(target_price_RngThru,target_price_TurnOvr)
                volume_today = get_volume_today(Markets_List[j])
                volume_ystday = get_volume_ystday(Markets_List[j])
                time.sleep(0.2)
                print(Markets_List[j])

                if current_price > min(target_price_RngThru,target_price_TurnOvr): #and volume_today > volume_ystday
                    krw_bal = get_balance("KRW") #Bring balance
                    if krw_bal > 5000:
                        upbit.buy_market_order(Markets_List[k], krw_bal*0.9995) #BUY
                        print("Coin:%s || Current Price:%f || Target Price:%f" %(Markets_List[j],current_price,target_price_OverAll))
                        print("Yesterday Volume:%f || Today Volume:%f" %(volume_ystday,volume_today))
                        print("******Purchased******",Markets_List[j],now)
                        Purchased.append(Markets_List[j])
                        Markets_List.remove(Markets_List[j])
                                                
            # else:
            #     p += 1
            #     print(p)
        #Tomorrow 08:59:30 < Current time < 08:59:45 : SELL
        elif end_time - datetime.timedelta(seconds=30) < now < end_time - datetime.timedelta(seconds=15):
                for k in range(0,len(Purchased)):
                    sell_bal = get_balance(Purchased[k]) # Bring Balance
                    if sell_bal > 0.0005:
                        upbit.sell_market_order(Purchased[k], sell_bal*0.9995)
                        print("The Coin has been sold",now)
        
        #Tomorrow 08:59:45 < Current Time < 09:00:00 : Reset all
        elif end_time - datetime.timedelta(seconds=15) < now < end_time:
            Markets_List = ['KRW-XRP','KRW-ETC','KRW-BTC']
            Purchased = [ ]

        time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(1)

