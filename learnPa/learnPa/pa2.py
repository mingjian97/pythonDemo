#！/usr/bin/env python
# -*- coding:utf-8 -*-
# author:mingjian time:2019/10/4
'''
requests 登录github
'''
import requests
import re

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Origin': 'https://github.com',
    'Upgrade-Insecure-Requests': '1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://github.com/session',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}


s=requests.session()
s.headers.update(headers)


def get_token():
    url='https://github.com/login'
    response=s.get(url)
    pat='name=\"authenticity_token\" value=\"(.*?)\"'
    authenticity_token=re.findall(pat,response.text)[0]
    return authenticity_token


def login(authenticity_token,account,password):
    payload={
        'commit':'Sign in',
        'utf8':'\u2713',
        'authenticity_token': authenticity_token,
        'login': account,
        'password': password,
    }
    url='https://github.com/session'
    response=s.post(url,data=payload)
    print(response)


if __name__=='__main__':
    account,password='1400017201@qq.com','wmj341223'
    authenticity_token=get_token()
    login(authenticity_token,account,password)