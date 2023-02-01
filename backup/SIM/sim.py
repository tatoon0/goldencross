import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas_datareader import data

n = 6 # 페이지당 50종목

code = [] # 종목코드
name = [] # 종목이름

for i in range(1,n+1):
    web = requests.get(f"https://finance.naver.com/sise/sise_market_sum.naver?&page={i}") # 네이버증권 시가총액 페이지
    print(web)
    soup = BeautifulSoup(web.content, 'html.parser')

    source = soup.select('a.tltle')

    for j in source:
        code.append(re.findall('\d\d\d\d\d\d', j['href'])[0])
        name.append(j.text)

# for i in range(n*50):
#     print(f'{name[i]} : {code[i]}')

total = [] # 최종 결과
for i in range(n*50):
    df = data.DataReader(code[i],'naver',start='2019-01-01')
    Avg5 = df['Close'].rolling(5).mean() # 5일 이동평균
    Avg20 = df['Close'].rolling(20).mean() # 20일 이동평균

    t = [] # 골든크로스, 데드크로스 시점

    state = 'd' # d = 데드크로스 / g = 골든크로스
    Bprice = 0 # 매수가
    Sprice = 0 # 매도가
    profit = [] # 손익

    for j in range(21, len(df)):
        if state == 'd' and Avg5[j-1] <= Avg20[j-1] and Avg5[j] > Avg20[j]: # 골든크로스 시점에 매수
            Bprice = df['Close'][j] # 매수가 기록
            # print(f'buy : {Bprice}')
            state = 'g'
        if state == 'g' and Avg5[j-1] >= Avg20[j-1] and Avg5[j] < Avg20[j]: # 데드크로스 시점에 매도
            Sprice = df['Close'][j] # 매도가 기록
            # print(f'sell : {Sprice}')
            state = 'd'
            profit.append(int(Sprice) - int(Bprice)) # 손익계산
            # print(f'income : {income}\n')
    
    total.append(sum(profit)) # 손익 기록
    print(f'{name[i]} : {sum(profit)}')

print(sum(total)) # 최종 결과