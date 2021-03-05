#   This file is part of the ecoAlert project.
#   Copyright (c) 2021 John Lyu
#   All Rights Reserved.
#   Unauthorized copying of this file, via any medium is strictly prohibited
#   Proprietary and confidential

from kafka import KafkaConsumer

class SmsMessenger(object):
    """Documents for SmsMessenger"""
    BASE_JSON = {
        "badge": "",
        "content": "",
        "custom": {},
        "insertDB": "1",
        "khhs": "",
        "mobiles": "18510486803",
        "msgCategory": 1,
        "msgDeadTime": "", #"201708111500",
        "msgType": "SMS",
        "secretLevel": "0",
        "silent": "0",
        "targetUserPushMode": "MOBILE",
        "title": "吕春回标题按khh推送通知",
        "userNOs": ""
    }

    def __init__(self, ):
        """Constructor for SmsMessenger"""
        # To consume latest messages and auto-commit offsets
        self.consumer = KafkaConsumer('my-topic',
                                 group_id='my-group',
                                 bootstrap_servers=['localhost:9092'])

    def get_alerts(self, ):
        for message in self.consumer:
            # message value and key are raw bytes -- decode if necessary!
            # e.g., for unicode: `message.value.decode('utf-8')`
            print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                 message.offset, message.key,
                                                 message.value))