
from bs4 import BeautifulSoup
from urllib.request import urlopen


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

