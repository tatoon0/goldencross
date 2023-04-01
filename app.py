import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas_datareader import data
from datetime import datetime, timedelta

n = 6 # 페이지당 50종목

code = [] # 종목코드
name = [] # 종목이름
state_short = [] # 단기상태
state_long = [] # 장기상태
Yesterday5 = [] # 전일 5일 이동평균
Yesterday20 = [] # 전일 20일 이동평균
TodayAvg5 = [] # 금일 5일 이동평균
TodayAvg20 = [] # 금일 20일 이동평균
Yesterday60 = [] # 전일 60일 이동평균
Yesterday120 = [] # 전일 120일 이동평균
TodayAvg60 = [] # 금일 60일 이동평균
TodayAvg120 = [] # 금일 120일 이동평균
Close = [] # 종가
link = [] # 링크

for i in range(1,n+1):
    web = requests.get(f"https://finance.naver.com/sise/sise_market_sum.naver?&page={i}") # 네이버증권 시가총액 페이지
    print(web)
    soup = BeautifulSoup(web.content, 'html.parser', from_encoding='cp949')

    source = soup.select('a.tltle')

    for j in source:
        code.append(re.findall('\d\d\d\d\d\d', j['href'])[0])
        name.append(j.text)
        link.append(f'https://finance.naver.com{j["href"]}')

date = datetime.now() - timedelta(days=200)
for i in range(n*50):
    df = data.DataReader(code[i],'naver',start=date.strftime('%Y-%m-%d'))
    Close.append(df['Close'][len(df)-1])
    Avg5 = df['Close'].rolling(5).mean() # 5일 이동평균
    Avg20 = df['Close'].rolling(20).mean() # 20일 이동평균
    Avg60 = df['Close'].rolling(60).mean() # 60일 이동평균
    Avg120 = df['Close'].rolling(120).mean() # 120일 이동평균

    Yesterday5.append(Avg5[len(Avg5)-2])
    Yesterday20.append(Avg20[len(Avg20)-2])
    Yesterday60.append(Avg60[len(Avg60)-2])
    Yesterday120.append(Avg120[len(Avg120)-2])

    TodayAvg5.append(Avg5[len(Avg5)-1])
    TodayAvg20.append(Avg20[len(Avg20)-1])
    TodayAvg60.append(Avg60[len(Avg60)-1])
    TodayAvg120.append(Avg120[len(Avg120)-1])
    
    if TodayAvg5[i] < TodayAvg20[i]:
        if Yesterday5[i] >= Yesterday20[i]:
            state_short.append('DEAD')
        else:
            state_short.append('D')
    elif TodayAvg5[i] > TodayAvg20[i]:
        if Yesterday5[i] <= Yesterday20[i]:
            state_short.append('GOLD')
        else:
            state_short.append('G')
    else:
        state_short.append('T')

    if TodayAvg60[i] < TodayAvg120[i]:
        if Yesterday60[i] >= Yesterday120[i]:
            state_long.append('DEAD')
        else:
            state_long.append('D')
    elif TodayAvg60[i] > TodayAvg120[i]:
        if Yesterday60[i] <= Yesterday120[i]:
            state_long.append('GOLD')
        else:
            state_long.append('G')
    else:
        state_long.append('T')    

profile = {
    '종목이름' : name,
    '종목코드' : code,
    '단기상태' : state_short,
    '장기상태' : state_long,
    '5일 이동평균' : TodayAvg5,
    '20일 이동평균' : TodayAvg20,
    '60일 이동평균' : TodayAvg60,
    '120일 이동평균' : TodayAvg120,
    '종가' : Close,
    '링크' : link
}

holdingStockCode = [
    '000660'
    ]

def holding(code):
    if code in holdingStockCode:
        return 'O'
    else:
        return 'X'

df = pd.DataFrame(profile)
df['보유여부'] = df['종목코드'].apply(holding)
df.to_excel(f'{datetime.now().strftime("%Y-%m-%d")}.xlsx', index=False)
