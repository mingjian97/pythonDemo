# -*- coding: utf-8 -*-
import scrapy
from pyquery import PyQuery
from ..items import City58Item
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider

class City58TestSpider(RedisSpider):
    name = 'city58_test'
    allowed_domains = ['58.com']
    start_urls = ['https://bj.58.com/chuzu/']

    def parse(self, response):
        jpy = PyQuery(response.text)
        li_list=jpy('body > div.list-wrap > div.list-box > ul > li').items()
        for it in li_list:
            a_tag=it(' div.des > h2 > a')
            item=City58Item()
            item['name']=a_tag.text()
            item['url']=a_tag.attr('href')
            item['price']=it('div.list-li-right > div.money > b').text()

            print(item['price'])
            yield item

        if not li_list:
            return
        pn =response.meta.get('pn',1)
        pn+=1
        response.meta['pn']=pn
        if pn>6:
            return
        req = response.follow('/chuzu/pn{}/'.format(pn),callback=self.parse,meta=response.meta)
        yield req
        #
        # test_request1 = Request('https://bj.58.com/chuzu/pn3',
        #                         callback=self.parse,
        #                         errback=self.error_back,
        #                         headers={},
        #                         cookies={},
        #                         priority=10,
        #                         )
        #
        # test_request2 = Request('https://58.com',
        #                         callback=self.parse,
        #                         errback=self.error_back,
        #                         priority=10,
        #                         meta={'dont_redirect':True}
        #                         )
        #
        # test_request3 = Request('https://58.com',
        #                         callback=self.parse,
        #                         errback=self.error_back,
        #                         priority=10,
        #                         # meta={'dont_redirect': True}
        #                         )
        #
        # yield test_request1
        # yield test_request2
        # yield test_request3

    def error_back(self,e):
        _=self
        print(e)
        print('我报错了')