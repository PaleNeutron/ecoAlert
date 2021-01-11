#   This file is part of the ecoAlert project.
#   Copyright (c) 2020 John Lyu
#   All Rights Reserved.
#   Unauthorized copying of this file, via any medium is strictly prohibited
#   Proprietary and confidential

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from sqlalchemy.orm import sessionmaker
from kafka import KafkaProducer
from kafka.errors import KafkaError

from ecoAlert.models import db_connect, create_table, Announcement


class BaseDBPipeline(object):
    """提供储存到数据库的pipeline的基础组件"""

    def __init__(self):
        # Initializes database connection and sessionmaker.
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def close_spider(self, spider):
        # 这个方法会在pipeline结束时自动调用
        # We commit and save all items to DB when spider finished scraping.
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()


class DatabasePipeline(BaseDBPipeline):
    """将爬虫结果储存到数据库中的管道, 基于ORM模型, 可适应不同种类的数据库"""

    def process_item(self, item, spider: "scrapy.Spider"):
        # 因为Announcement类中存在一个id字段作为pk, 因此, 从爬取的数据中删掉id
        if "id" in item:
            del item["id"]
        # check if item with this title exists in DB
        item_exists = self.session.query(Announcement).filter_by(announcementTitle=item['announcementTitle']).first()
        # if item exists in DB - we just update it
        if item_exists:
            # 可以在这里编写对重复抓取的内容的处理方式
            # item_exists.secCode = item['secCode']
            # spider.logger.debug('Item {} updated.'.format(item['announcementTitle']))
            item_exists.update(**item)
            # pass
        # if not - we insert new item to DB
        else:
            new_item = Announcement(**item)
            self.kafka_send("topic", b'message', spider)
            self.session.add(new_item)
            spider.logger.debug('New item {} added to DB.'.format(item['announcementTitle']))
        return item

    def kafka_send(self, topic, message, spider: "scrapy.Spider"):

        producer = KafkaProducer(bootstrap_servers=['broker1:1234'])

        # Asynchronous by default
        future = producer.send('my-topic', b'raw_bytes')

        # Block for 'synchronous' sends
        try:
            record_metadata = future.get(timeout=10)
            # Successful result returns assigned partition and offset
            spider.logger.debug(record_metadata.topic)
            spider.logger.debug(record_metadata.partition)
            spider.logger.debug(record_metadata.offset)
        except KafkaError:
            # Decide what to do if produce request failed...
            spider.logger.exception()
            return


class KafkaPipeline:
    """从数据中提取message发送到kafka中"""
    def process_item(self, item, spider):
        return item


class EcoalertPipeline:
    """default pipline"""

    def process_item(self, item, spider):
        return item
