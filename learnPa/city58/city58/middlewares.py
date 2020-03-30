# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import scrapy.downloadermiddlewares.retry

class UAMiddleware(object):

    ua_list=['Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
             'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
             'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
             ]

    def process_request(self,request,spider):
        request.headers['User-Agent']=random.choices(self.ua_list)
        print(request.url)
        print(request.headers['User-Agent'])

    def process_response(self,request,response,spider):

        return response

    def process_exception(self,request,exception,spider):
        pass