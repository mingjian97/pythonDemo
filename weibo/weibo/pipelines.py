# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from pymongo.errors import DuplicateKeyError
from weibo.settings import LOCAL_MONGO_HOST,LOCAL_MONGO_PORT,DB_NAME
from weibo.items import RelationshipItem,TweetsItem,CommentItem,UserInformationItem

class MongoDBPipeline(object):
    def __init__(self):
        client=pymongo.MongoClient(LOCAL_MONGO_HOST,LOCAL_MONGO_PORT)
        db=client[DB_NAME]
        self.Information=db['Information']
        self.Tweets=db['Tweets']
        self.Comments=db['Comments']
        self.Relationships=db['Relationships']

    def process_item(self,item,spider):
        '''判断item的类型，并作相应的处理，再入数据库'''
        if isinstance(item,RelationshipItem):
            self.insert_item(self.Relationships,item)
        elif isinstance(item,TweetsItem):
            self.insert_item(self.Tweets,item)
        elif isinstance(item,UserInformationItem):
            self.insert_item(self.Information,item)
        elif isinstance(item,CommentItem):
            self.insert_item(self.Comments,item)
        return item


    @staticmethod
    def insert_item(collection,item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            '''
            说明有重复数据
            '''
            pass