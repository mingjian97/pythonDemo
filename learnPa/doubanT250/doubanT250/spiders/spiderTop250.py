# -*- coding: utf-8 -*-

'''
爬取豆瓣电影TOP250
保存到数据库中
项目使用了scrapy
选择器使用了pyquery
date：2019/10/6
'''

import scrapy
from scrapy.http import Request
from pyquery import PyQuery
from ..items import Doubant250Item

class Spidertop250Spider(scrapy.Spider):
    name = 'spiderTop250'
    allowed_domains = ['movie.douban.com']
    start_urls = ['http://movie.douban.com/top250/']

    def parse(self, response):
        item=Doubant250Item()
        jpy=PyQuery(response.text)
        movie_list=jpy('#content > div > div.article > ol > li').items()
        for it in movie_list:
            item['title']=it('div > div.info > div.hd > a').text()
            item['movieInfo']=it('div > div.info > div.bd > p:nth-child(1)').text()
            item['star']=it('div > div.info > div.bd > div > span.rating_num').text()
            quotee=it('div > div.info > div.bd > p.quote > span').text()
            if quotee:
                item['quote']=quotee
            else:
                item['quote'] =''

            yield item

            nextLink=jpy('#content > div > div.article > div.paginator > span.next > a')
            if nextLink:
                nextLink=nextLink.attr('href')
                yield response.follow('/top250/'+nextLink,callback=self.parse)

