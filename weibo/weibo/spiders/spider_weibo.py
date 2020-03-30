# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from weibo.items import UserInformationItem,TweetsItem,RelationshipItem,CommentItem
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from lxml import etree
import time
import re
from weibo.spiders.utils import time_fix,extract_weibo_content,extract_comment_content
'''
url示例：
用户信息页： https://weibo.cn/2803301701/info
用户发布的微博的界面：https://weibo.cn/u/2803301701
                    https://weibo.cn/u/2803301701?page=2
            or：    https://weibo.cn/2803301701?page=2
                    https://weibo.cn/2803301701/profile?page=1

用户的关注列表：https://weibo.cn/2803301701/follow?page=1

用户的粉丝列表：https://weibo.cn/2803301701/fans?page=1


'''
class SpiderWeiboSpider(scrapy.Spider):
    name = 'spider_weibo'
    allowed_domains = ['weibo.cn']
    # start_urls = ['http://weibo.cn/']
    base_url="https://weibo.cn"

    # #测试评论
    # def start_requests(self):
    #     yield Request(url='https://weibo.cn/comment/Ib7c5FQyd?page=1',callback=self.parse_comment,
    #                   meta={'weibo_url':'https://weibo.com/2803301701/Ib7c5FQyd'})

    def start_requests(self):
        start_uids = [
            # '2803301701',  # 人民日报
            '1699432410'  # 新华社
        ]
        for uid in start_uids:
            yield Request('https://weibo.cn/%s/info'%uid,callback=self.parse_information)

    def parse_information(self, response):
        '''抓取个人信息'''
        infoItem = UserInformationItem()
        infoItem['crawl_time'] = int(time.time())
        selector = Selector(response)
        infoItem['_id'] = re.findall('(\d+)/info', response.url)[0]
        text1 = ";".join(selector.xpath('//div[@class="c"]//text()').extract())  # 获取标签里所有的text()
        nick_name = re.findall('昵称;?[：:]?(.*?);', text1)
        gender = re.findall('性别;?[：:]?(.*?);', text1)
        place = re.findall('地区;?[：:]?(.*?);', text1)
        birthday = re.findall('生日;?[：:]?(.*?);', text1)
        briefIntroduction = re.findall('简介;?[：:]?(.*?);', text1)
        sex_orientation = re.findall('性取向;?[：:]?(.*?);', text1)
        sentiment = re.findall('感情状况;?[：:]?(.*?);', text1)
        vip_level = re.findall('会员等级;?[：:]?(.*?);', text1)
        authentication = re.findall('认证;?[：:]?(.*?);', text1)
        labels = re.findall('标签;?[：:]?(.*?)更多>>', text1)
        if nick_name and nick_name[0]:
            infoItem['nick_name'] = nick_name[0].replace(u'\xa0', '')  # \xa0 是不间断空白符
        if gender and gender[0]:
            infoItem['gender'] = gender[0].replace(u'\xa0', '')
        if place and place[0]:
            place = place[0].replace(u'\xa0', '').split(" ")
            infoItem['province'] = place[0]
            if len(place)>1:
                infoItem['city'] = place[1]
        if briefIntroduction and briefIntroduction[0]:
            infoItem['brief_introduction'] = briefIntroduction[0].replace(u'\xa0', '')
        if birthday and birthday[0]:
            infoItem['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u'\xa0', '') == gender[0]:
                infoItem['sex_orientation'] = '同性恋'
            else:
                infoItem['sex_orientation'] = '异性恋'
        if sentiment and sentiment[0]:
            infoItem['sentiment'] = sentiment[0].replace(u'\xa0', '')
        if vip_level and vip_level[0]:
            infoItem['vip_level'] = vip_level[0].replace(u'\xa0', '')
        if authentication and authentication[0]:
            infoItem['authentication'] = authentication[0].replace(u'\xa0', '')
        if labels and labels[0]:
            infoItem['labels'] = labels[0].replace(u'\xa0', '').strip(',')

        request_meta = response.meta
        request_meta['item'] = infoItem
        yield Request(self.base_url+'/u/{}'.format(infoItem['_id']),
                      callback=self.parse_further_information,
                      meta=request_meta,
                      dont_filter=True,
                      priority=1)

    def parse_further_information(self, response):
        text=response.text
        infoItem=response.meta['item']
        tweets_num=re.findall('微博\[(\d+)\]',text)
        if tweets_num:
            infoItem['tweets_num']=int(tweets_num[0])
        follows_num=re.findall('关注\[(\d+)\]',text)
        if follows_num:
            infoItem['follows_num']=int(follows_num[0])
        fans_num=re.findall('粉丝\[(\d+)\]',text)
        if fans_num:
            infoItem['fans_num']=int(fans_num[0])
        yield infoItem

        # #获取该用户微博
        # yield Request(url=self.base_url+'/{}/profile?page=1'.format(infoItem['_id']),
        #               callback=self.parse_tweet,
        #               priority=1)
        # #获取关注列表
        # yield Request(url=self.base_url+'/{}/follow?page=1'.format(infoItem['_id']),
        #               callback=self.parse_follow,
        #               dont_filter=True)
        #获取粉丝列表
        yield Request(url=self.base_url+'/{}/fans?page=1'.format(infoItem['_id']),
                      callback=self.parse_fans,
                      dont_filter=True)

    def parse_tweet(self,response):
        if response.url.endswith('page=1'):
            #如果是第一页，一次性获取后面的所有页
            all_page=re.search(r'>&nbsp;1/(\d+)页</div>',response.text)
            if all_page:
                all_page=all_page.group(1)
                all_page=int(all_page)
                for page_num in range(2,all_page+1):
                    page_url=response.url.replace('page=1','page={}'.format(page_num))
                    yield Request(page_url,self.parse_tweet,dont_filter=True,meta=response.meta)
        #解析本页的所有数据
        tree_node=etree.HTML(response.body)
        tweet_nodes=tree_node.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweetItem=TweetsItem()
                tweetItem['crawl_time']=int(time.time())
                tweet_repost_url=tweet_node.xpath('//a[contains(text(),"转发[")]/@href')[0]
                user_tweet_id=re.search(r'/repost/(.*?)\?uid=(\d+)',tweet_repost_url)
                tweetItem['weibo_url']='https://weibo.com/{}/{}'.format(user_tweet_id.group(2),user_tweet_id.group(1))
                tweetItem['user_id']=user_tweet_id.group(2)
                tweetItem['_id']='{}_{}'.format(user_tweet_id.group(2),user_tweet_id.group(1))
                create_time_info_node=tweet_node.xpath('//span[@class="ct"]')[-1]
                create_time_info=create_time_info_node.xpath('string(.)')
                if "来自" in create_time_info:
                    tweetItem['created_at']=time_fix(create_time_info.split('来自')[0].strip())
                    tweetItem['tool']=create_time_info.split('来自')[1].strip()
                else :
                    tweetItem['created_at']=time_fix(create_time_info.strip())

                like_num=tweet_node.xpath('//a[contains(text(),"赞[")]/text()')[-1]
                tweetItem['like_num']=int(re.search('\d+',like_num).group())
                repost_num=tweet_node.xpath('//a[contains(text(),"转发[")]/text()')[-1]
                tweetItem['repost_num']=int(re.search('\d+',repost_num).group())

                comment_num=tweet_node.xpath(
                    '//a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()')[-1]
                tweetItem['comment_num']=int(re.search('\d+',comment_num).group())
                images=tweet_node.xpath('//img[@alt="图片"]/@src')
                if images:
                    tweetItem['image_url']=images[0]

                videos=tweet_node.xpath('//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweetItem['video_url']=videos[0]
                map_node=tweet_node.xpath('//a[contains(text(),"显示地图")]')
                if map_node:
                    map_node=map_node[0]
                    map_node_url=map_node.xpath('/@href')[0]
                    map_info=re.search(r'xy=(.*?)&',map_node_url).group(1)
                    tweetItem['location_map_info']=map_info

                repost_node=tweet_node.xpath('//a[contains(text(),"原文评论")]/@href')
                if repost_node:
                    tweetItem['origin_weibo']=repost_node[0]

                #检测有没有阅读全文
                all_content_link=tweet_node.xpath('//a[text()="全文" and contains(@href,ckAll=1)]')
                if all_content_link:
                    all_content_url=self.base_url+all_content_link[0].xpath('/@href')[0]
                    yield Request(all_content_url,callback=self.parse_all_content,
                                  meta={'item':tweetItem},
                                  priority=1)
                else:
                    tweet_html=etree.tostring(tweet_node,encoding='unicode')
                    tweetItem['content']=extract_weibo_content(tweet_html)
                    yield tweetItem

                # #抓取微博的评论信息
                # comment_url=self.base_url+'/comment/'+tweetItem['weibo_url'].split('/')[-1]+'?page=1'
                # yield Request(url=comment_url,callback=self.parse_comment,
                #               meta={'weibo_url':tweetItem['weibo_url']})

            except Exception as e:
                self.logger.error(e)

    def parse_all_content(self,response):
        #有阅读全文的情况下，获取全文
        tree_node=etree.HTML(response.body)
        tweetItem=response.meta['item']
        content_node=tree_node.xpath('//*[@id="M_"]/div[1]')[0]
        tweet_html=etree.tostring(content_node,encoding='unicode')
        tweetItem['content']=extract_weibo_content(tweet_html)
        yield tweetItem


    def parse_follow(self,response):
        '''抓取关注列表'''
        if response.url.endswith('page=1'):
            all_page=re.search(r'>&nbsp;1/(\d+)页</div>',response.text)
            if all_page:
                all_page=all_page.group(1)
                all_page=int(all_page)
                for page_num in range(2,all_page+1):
                    page_url=response.url.replace('page=1','page={}'.format(page_num))
                    yield Request(page_url,self.parse_follow,dont_filter=True,
                                  meta=response.meta)
        selector=Selector(response)
        urls=selector.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
        uids=re.findall('uid=(\d+)',";".join(urls),re.S)
        ID=re.findall('(\d+)/follow',response.url)[0]
        for uid in uids:
            relationshipsItem=RelationshipItem()
            relationshipsItem['crawl_time']=int(time.time())
            relationshipsItem['fan_id']=ID
            relationshipsItem['followed_id']=uid
            relationshipsItem['_id']=ID+'-'+uid
            yield relationshipsItem


    def parse_fans(self,response):
        '''抓取粉丝列表'''
        if response.url.endswith('page=1'):
            all_page=re.search(r'>&nbsp;1/(\d+)页</div>',response.text)
            if all_page:
                all_page=all_page.group(1)
                all_page=int(all_page)
                for page_num in range(2,all_page+1):
                    page_url=response.url.replace('page=1','page={}'.format(page_num))
                    yield Request(page_url,self.parse_fans,dont_filter=True,
                                  meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="移除"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/fans', response.url)[0]
        for uid in uids:
            relationshipsItem = RelationshipItem()
            relationshipsItem['crawl_time'] = int(time.time())
            relationshipsItem["fan_id"] = uid
            relationshipsItem["followed_id"] = ID
            relationshipsItem["_id"] = uid + '-' + ID
            yield relationshipsItem

    def parse_comment(self,response):
        if response.url.endswith('page=1'):
            all_page=re.search(r'>&nbsp;1/(\d+)页</div>',response.text)
            if all_page:
                all_page=all_page.group(1)
                all_page=int(all_page)
                for page_num in range(2,all_page+1):
                    page_url=response.url.replace('page=1','page={}'.format(page_num))
                    yield Request(page_url,self.parse_comment,dont_filter=True,meta=response.meta)
        tree_node=etree.HTML(response.body)
        comment_nodes=tree_node.xpath('//div[@class="c" and contains(@id,"C_")]')
        for comment_node in comment_nodes:
            comment_user_url=comment_node.xpath('a[contains(@href,"/u/")]/@href')
            if not comment_user_url:
                continue
            commentItem=CommentItem()
            commentItem['crawl_time']=int(time.time())
            commentItem['weibo_url']=response.meta['weibo_url']
            commentItem['comment_user_id']=re.search(r'/u/(\d+)',comment_user_url[0]).group(1)
            commentItem['content']=extract_comment_content(etree.tostring(comment_node,encoding='unicode'))
            commentItem['_id']=comment_node.xpath('./@id')[0]
            created_at_info =comment_node.xpath('span[@class="ct"]/text()')[0]
            like_num=comment_node.xpath('//a[contains(text(),"赞[")]/text()')[-1]
            commentItem['like_num']=int(re.search('\d+',like_num).group())
            commentItem['created_at']=time_fix(created_at_info.split('\xa0')[0])
            yield commentItem

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl('spider_weibo')
    process.start()

