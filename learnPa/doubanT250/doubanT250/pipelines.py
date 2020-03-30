# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class Doubant250Pipeline(object):

    def __init__(self):
        self.connect=pymysql.connect(
            host='localhost',
            db='doubanmovie',
            user='root',
            passwd='123'
        )
        self.cursor=self.connect.cursor()
        print('连接数据库')

    def process_item(self, item, spider):
        try:
            self.cursor.execute(
                """insert into movie(title,movieInfo,star,quote) value(%s,%s,%s,%s)""",
                (item['title'],item['movieInfo'],item['star'],item['quote'])
                )
            self.connect.commit()
        except Exception as e:
            print("重复插入了==>错误信息为：" + str(e))
        return item
