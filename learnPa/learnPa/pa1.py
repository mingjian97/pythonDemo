# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# author:mingjian time:2019/10/4
'''
selenium 登录github
'''
import time
from selenium import webdriver


driver=webdriver.Chrome()
driver.maximize_window()


def login(account,password):
    driver.get('https://github.com/login')
    time.sleep(2)
    driver.find_element_by_id('login_field').send_keys(account)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_xpath('//input[@class="btn btn-primary btn-block"]').click()


if __name__=='__main__':
    account,password='1400017201@qq.com','wmj3411223'
    login(account,password)



