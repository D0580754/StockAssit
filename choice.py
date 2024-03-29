
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import pandas as pd
import datetime

def techface(name):
    html = urlopen('http://tw.stock.yahoo.com/d/i/rank.php?t='+name+'&e=tse&n=5')
    soup = BeautifulSoup(html)
    a=[]
    b=[]
    for i in soup.find_all('td',class_='name'):
        a.append(i.a.contents)
    for i in range(10):
        b.append(str(a[i]))

    c = '\n'.join(b)

    return c
def chipface(name):
    html = urlopen('https://fubon-ebrokerdj.fbs.com.tw/Z/ZG/'+name+'.djhtm')
    soup = BeautifulSoup(html)
    a=[]
    b=[]
    for i in soup.find_all('td',class_='t3t1'):
        a.append(i.a.text)
    for i in range(10):
        b.append(str(a[i]))

    c = '\n'.join(b)

    return c

def basicface(name):
        #最近一個月營收創新高
    html = urlopen('https://concords.moneydj.com/z/zk/zk2/'+name+'.djhtm')
    soup = BeautifulSoup(html)
    a=[]
    for i in soup.find_all('td',class_='zkt1L'):
        a.append(i.a.text)

    c = '\n'.join(a)
    
    return c
def EPSBPR():
    try:

        a = datetime.datetime.today() + datetime.timedelta(-1)
        date = a.strftime('%Y%m%d')
        #date = '20191129'
        html = urlopen('http://www.tse.com.tw/exchangeReport/BWIBBU_d?response=json&date='+date+'&selectType=ALL')
        jcontent = json.loads(html.read())
        data = jcontent['data']
        data = [i for i in data if i[4]!='-']
        Dividend_list = sorted(data , key=lambda x: float(x[2].replace(',','')),reverse=True)[:100]
        #columns
        df = pd.DataFrame(jcontent['data'])
        df.columns = ['證券代號','證券名稱','殖利率(%)','股利年度','本益比',
                        '股價淨值比','財報年/季']
        PBR = pd.to_numeric(df['股價淨值比'], errors='coerce') < 0.7 # 找到股價淨值比小於0.7的股票
        EPS = pd.to_numeric(df['本益比'], errors='coerce') < 10 # 找到本益比小於13的股票
        candidate= df[(PBR & EPS)]
        a=[]
        for i in candidate['證券名稱']:
            a.append(i)

        c = '\n'.join(a)
        return c
    except:
        c = "目前沒有資訊"
        return c
def y_ield():
    html = urlopen('https://statementdog.com/screeners/dividend_yield_ranking')
    soup = BeautifulSoup(html)
    a=[]
    c=[]
    for i in soup.find_all('ul',class_='ranking-item'):
        a.append(i.a.text)


    for i in range(1,len(a)):
        c.append(a[i])


    c = '\n'.join(c)
    return c