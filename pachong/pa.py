# import urllib.request
# f=urllib.request.urlopen('http://www.baidu.com')
# print(f.read().decode('utf-8'))

import requests
from bs4 import BeautifulSoup

def getHTMLText(url):
    try:
        r=requests.get(url,timeout=20)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except :
        return '产生异常'

def getComments(r):
    data=[]
    soup=BeautifulSoup(r,'lxml')
    pattern=soup.find_all('span','short')
    for item in pattern:
        data.append(item.string)
    return data

if __name__=='__main__':
    url='http://book.douban.com/subject/1084336/comments'
    r=getHTMLText(url)
    comments=getComments(r)
    for item in comments:
        print(item)