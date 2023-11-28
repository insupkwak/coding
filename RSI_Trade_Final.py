import pyupbit
import talib
import pyupbit.websocket_api as wsck
import requests
import datetime



#초기설정 
access = "ys9AXnCJX1RRA17dUXKKU6xqnfInuXv4x5425cd6"
secret = "jt63eLxNZ9y07ezvTOXDlHLeLKBszVVkGun9Dbxd"
discord = "https://discord.com/api/webhooks/1176157989506404512/MPNnjvAJdhmsY37AGexHLQDwgUnekpRSRQKTWHC8_3PMQwrq1u0Z_wB_bR_b1BZHqnSx"


coin = "KRW-ONG"
coin_name = "ONG"
period = "minute5"
rsi_limit = 28
rsi_limit_minus = 5
profit = 2.0
initial_invest = 15000
additional_invest = 30000



#메시지 전송
def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%H:%M')}] {str(msg)}"}
    requests.post(discord, data=message)
    print(message)


#RSI 지표함수
def RSI(period = 14) :
    rdf = pyupbit.get_ohlcv(coin, period, 70)
    rdf['rsi'] = talib.RSI(rdf.close) #RSI 생성
    numlist = [] 
    for i in range(len(rdf)) :
        numlist.append(i)
    numlist.reverse()
    rdf['num'] = numlist #rdf 번호부여
    return rdf


preRSI = 0.0
masuCnt = 0 
btgCnt = 0.0 #비트코인 수량
btgAvg = 0.0 #비트코인 평단가 

if __name__ == "__main__" : 
    while True :
        try:

            #통신연결(본인이 원하는 코인 종류, 로 구분하여 쭉 나열해도 된다.)
            #대신 코인 종류를 여러개 설정하면 틱이 더욱 빈번하게 발생하여 시스템부하가 더 커짐 
            wm = wsck.WebSocketManager("ticker", [coin,])
            for i in range (1000) :
                
                #실시간 현재가
                data = wm.get()
                print(f"{i} 번째 자동매매")
           
                #1번째 RSI 지표 조회                             
                df = RSI()  
                rsiNum = df['rsi'].loc[(df.rsi <= rsi_limit) & (df.num == 0)].values
                print (df['rsi'].loc[df.num == 0].values)

                #본인 api 키 로그인
                upbit = pyupbit.Upbit(access , secret)

                #계좌잔고
                myBalance = upbit.get_balances()
        
                for i in range(len(myBalance)):

                    if str(myBalance[i]['currency']) == "KRW" :
                        print(f"KRW 잔고 : {myBalance[i]['balance']}원")
                        
                    if str(myBalance[i]['currency']) == coin_name :
                        print(f"{coin_name} 수량 : {myBalance[i]['balance']}개")
                        print(f"{coin_name} 평균단가 : {myBalance[i]['avg_buy_price']}원")
                        btgCnt = float(myBalance[i]['balance'])
                        btgAvg = float(myBalance[i]['avg_buy_price'])

                #매도 
                if btgCnt > 0 : #매수한 개수가 존재할 경우
                
                    #수익률 계산
                    tempPlusRate = round(((float(data['trade_price'])-float(btgAvg))/float(btgAvg))*100,2)
                    print (f"현재 수익률 : {tempPlusRate} %")

                    if tempPlusRate >= profit  :
                        buyResult = upbit.sell_limit_order(coin, float(data['trade_price']), btgCnt)
                        print (buyResult)
                        masuCnt = 0 #매수 초기화
                        preRSI = 0.0 #RSI 초기화
                            
                #최초 매수
                if masuCnt == 0 : #최초진입
                    if(len(rsiNum) > 0) :
                        print ("최초매수")                   

                        #매수수량                    
                        if data['trade_price'] != None : 
                            ea = float(initial_invest) / float(data['trade_price'])
                            ea = round(ea,8)
                            print ("매수수량 : ",ea)
                                    
                        #매수
                            buyResult = upbit.buy_limit_order(coin,float(data['trade_price']),ea)
                            print (buyResult)
                            masuCnt = masuCnt +1 #매수카운트
                            preRSI = float(rsiNum[0]) #현재 RSI진표
                        
                #최초가 아닌경우 추가매수 
                else :
                    if preRSI - rsi_limit_minus > float(rsiNum[0]) : 
                        print ("추가매수")

                        ea = float(additional_invest) / float(data['trade_price'])
                        ea = round(ea,8)
                        print ("추가매수수량 : ",ea)
                                    
                    #매수
                        buyResult = upbit.buy_limit_order(coin,float(data['trade_price']),ea)
                        print (buyResult)
                        masuCnt = masuCnt +1 #매수카운트
                        preRSI = float(rsiNum[0]) #현재 RSI진표
                    
            #통신종료
            wm.terminate()
        
        except Exception as e :
            print(e)
            wm.terminate()














                

















