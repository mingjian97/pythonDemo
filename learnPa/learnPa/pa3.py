#！/usr/bin/env python
# -*- coding:utf-8 -*-
# author:mingjian time:2019/10/5

import requests

response=requests.get('https://www.google.com')
print(response.text)