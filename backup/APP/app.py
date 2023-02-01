import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas_datareader import data
from datetime import datetime, timedelta

n = 1 # 페이지당 50종목

code = [] # 종목코드
name = [] # 종목이름
state = [] # 상태
Yesterday5 = [] # 전일 5일 이동평균
Yesterday20 = [] # 전일 20일 이동평균
TodayAvg5 = [] # 금일 5일 이동평균
TodayAvg20 = [] # 금일 20일 이동평균
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

date = datetime.now() - timedelta(days=50)
for i in range(n*50):
    df = data.DataReader(code[i],'naver',start=date.strftime('%Y-%m-%d'))
    Close.append(df['Close'][len(df)-1])
    Avg5 = df['Close'].rolling(5).mean() # 5일 이동평균
    Avg20 = df['Close'].rolling(20).mean() # 20일 이동평균

    Yesterday5.append(Avg5[len(Avg5)-2])
    Yesterday20.append(Avg20[len(Avg20)-2])

    TodayAvg5.append(Avg5[len(Avg5)-1])
    TodayAvg20.append(Avg20[len(Avg20)-1])
    
    if TodayAvg5[i] < TodayAvg20[i]:
        if Yesterday5[i] >= Yesterday20[i]:
            state.append('DEAD')
        else:
            state.append('D')
    elif TodayAvg5[i] > TodayAvg20[i]:
        if Yesterday5[i] <= Yesterday20[i]:
            state.append('GOLD')
        else:
            state.append('G')
    else:
        state.append('T')

profile = {
    '종목이름' : name,
    '종목코드' : code,
    '상태' : state,
    '5일 이동평균' : TodayAvg5,
    '20일 이동평균' : TodayAvg20,
    '종가' : Close,
    '링크' : link
}

df = pd.DataFrame(profile)
df.to_excel(f'{datetime.now().strftime("%Y-%m-%d")}.xlsx', index=False)