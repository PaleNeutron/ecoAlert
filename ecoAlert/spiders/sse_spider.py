#   This file is part of the ecoAlert project.
#   Copyright (c) 2021 John Lyu
#   All Rights Reserved.
#   Unauthorized copying of this file, via any medium is strictly prohibited
#   Proprietary and confidential

import json
from datetime import datetime
from .headers import MAC_HEADERS

import scrapy


# response 格式
# 其中result字段中0到5分别对应总体, 主板A, 主板B, 科创板, 股票回购
#
# {'actionErrors': [],
#  'actionMessages': [],
#  'errorMessages': [],
#  'errors': {},
#  'fieldErrors': {},
#  'isPagination': 'false',
#  'jsonCallBack': None,
#  'locale': 'en_US',
#  'pageHelp': {'beginPage': 1,
#   'cacheSize': 5,
#   'data': None,
#   'endDate': None,
#   'endPage': None,
#   'objectResult': None,
#   'pageCount': None,
#   'pageNo': 1,
#   'pageSize': 10,
#   'searchDate': None,
#   'sort': None,
#   'startDate': None,
#   'total': 0},
#  'pageNo': None,
#  'pageSize': None,
#  'queryDate': '',
#  'result': [{'NEGOTIABLE_VALUE_FULL': '359504.2692725033',
#    'EXCHANGE_RATE': '0.9981',
#    'AVG_PROFIT_RATE': '15.47',
#    'AVG_PROFIT_RATE_FULL': '15.472',
#    'MKT_VALUE': '409691.14',
#    'TX_AMOUNT': '3588.38',
#    'TOTAL_MK_CAP_RATE': '0.8759',
#    'EXCHANGE_RATE_FULL': '0.9981',
#    'TX_NUM': '1579',
#    'TX_VOLUME_FULL': '308.04617261',
#    'NEGOTIABLE_VALUE': '359504.27',
#    'PRODUCT_TYPE': '1',
#    'CAL_DATE': '2020-12-29 00:00:00.0',
#    'MKT_VALUE_FULL': '409691.1442023049',
#    'TRADING_TX': '2258.5957',
#    'TX_AMOUNT_FULL': '3588.38256692',
#    'TX_VOLUME': '308.05',
#    'SUB_NEW_STOCK_RATE': '1.1327',
#    'TRADING_TX_FULL': '2258.5957',
#    'DEPOSIT_VOL': '-'},
#   {'NEGOTIABLE_VALUE_FULL': '369576.5914113647',
#    'EXCHANGE_RATE': '1.0422',
#    'AVG_PROFIT_RATE': '16.28',
#    'AVG_PROFIT_RATE_FULL': '16.279',
#    'MKT_VALUE': '441826.24',
#    'TX_AMOUNT': '3863.71',
#    'TOTAL_MK_CAP_RATE': '0.8718',
#    'EXCHANGE_RATE_FULL': '1.0422',
#    'TX_NUM': '1839',
#    'TX_VOLUME_FULL': '315.86465828',
#    'NEGOTIABLE_VALUE': '369576.59',
#    'PRODUCT_TYPE': '12',
#    'CAL_DATE': '2020-12-29 00:00:00.0',
#    'MKT_VALUE_FULL': '441826.2433490943',
#    'TRADING_TX': '2341.3103',
#    'TX_AMOUNT_FULL': '3863.70785828',
#    'TX_VOLUME': '315.86',
#    'SUB_NEW_STOCK_RATE': '1.0189',
#    'TRADING_TX_FULL': '2341.3103',
#    'DEPOSIT_VOL': '-'},
#   {'NEGOTIABLE_VALUE_FULL': '667.9766573441',
#    'EXCHANGE_RATE': '0.1599',
#    'AVG_PROFIT_RATE': '8.13',
#    'AVG_PROFIT_RATE_FULL': '8.132',
#    'MKT_VALUE': '667.98',
#    'TX_AMOUNT': '1.07',
#    'TOTAL_MK_CAP_RATE': '0.1599',
#    'EXCHANGE_RATE_FULL': '0.1599',
#    'TX_NUM': '48',
#    'TX_VOLUME_FULL': '0.24756116',
#    'NEGOTIABLE_VALUE': '667.98',
#    'PRODUCT_TYPE': '2',
#    'CAL_DATE': '2020-12-29 00:00:00.0',
#    'MKT_VALUE_FULL': '667.9766573441',
#    'TRADING_TX': '1.2657',
#    'TX_AMOUNT_FULL': '1.0681441',
#    'TX_VOLUME': '0.25',
#    'SUB_NEW_STOCK_RATE': '-',
#    'TRADING_TX_FULL': '1.2657',
#    'DEPOSIT_VOL': '-'},
#   {'NEGOTIABLE_VALUE_FULL': '369576.5914113647',
#    'EXCHANGE_RATE': '1.0422',
#    'AVG_PROFIT_RATE': '16.28',
#    'AVG_PROFIT_RATE_FULL': '16.279',
#    'MKT_VALUE': '441826.24',
#    'TX_AMOUNT': '3851.83',
#    'TOTAL_MK_CAP_RATE': '0.8718',
#    'EXCHANGE_RATE_FULL': '1.0422',
#    'TX_NUM': '1839',
#    'TX_VOLUME_FULL': '313.20665828',
#    'NEGOTIABLE_VALUE': '369576.59',
#    'PRODUCT_TYPE': '40',
#    'CAL_DATE': '2020-12-29 00:00:00.0',
#    'MKT_VALUE_FULL': '441826.2433490943',
#    'TRADING_TX': '2341.3093',
#    'TX_AMOUNT_FULL': '3851.82845828',
#    'TX_VOLUME': '313.21',
#    'SUB_NEW_STOCK_RATE': '1.0189',
#    'TRADING_TX_FULL': '2341.3093',
#    'DEPOSIT_VOL': '-'},
#   {'NEGOTIABLE_VALUE_FULL': '-',
#    'EXCHANGE_RATE': '0',
#    'AVG_PROFIT_RATE': '0',
#    'AVG_PROFIT_RATE_FULL': '0',
#    'MKT_VALUE': '-',
#    'TX_AMOUNT': '11.88',
#    'TOTAL_MK_CAP_RATE': '0',
#    'EXCHANGE_RATE_FULL': '0',
#    'TX_NUM': '-',
#    'TX_VOLUME_FULL': '2.658',
#    'NEGOTIABLE_VALUE': '-',
#    'PRODUCT_TYPE': '43',
#    'CAL_DATE': '2020-12-29 00:00:00.0',
#    'MKT_VALUE_FULL': '-',
#    'TRADING_TX': '0.001',
#    'TX_AMOUNT_FULL': '11.8794',
#    'TX_VOLUME': '2.66',
#    'SUB_NEW_STOCK_RATE': '-',
#    'TRADING_TX_FULL': '0.001',
#    'DEPOSIT_VOL': '-'},
#   {'NEGOTIABLE_VALUE_FULL': '9404.3454815173',
#    'EXCHANGE_RATE': '2.79',
#    'AVG_PROFIT_RATE': '90.32',
#    'AVG_PROFIT_RATE_FULL': '90.32',
#    'MKT_VALUE': '31467.12',
#    'TX_AMOUNT': '262.38',
#    'TOTAL_MK_CAP_RATE': '0.8338',
#    'EXCHANGE_RATE_FULL': '2.79',
#    'TX_NUM': '212',
#    'TX_VOLUME_FULL': '4.91292451',
#    'NEGOTIABLE_VALUE': '9404.35',
#    'PRODUCT_TYPE': '48',
#    'CAL_DATE': '2020-12-29 00:00:00.0',
#    'MKT_VALUE_FULL': '31467.1224894453',
#    'TRADING_TX': '81.4479',
#    'TX_AMOUNT_FULL': '262.37774726',
#    'TX_VOLUME': '4.91',
#    'SUB_NEW_STOCK_RATE': '0.912',
#    'TRADING_TX_FULL': '81.4479',
#    'DEPOSIT_VOL': '-'}],
#  'securityCode': '',
#  'sqlId': 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C',
#  'texts': None,
#  'type': '',
#  'validateCode': ''}


headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'http://www.sse.com.cn/',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
}

class SseSpider(scrapy.Spider):
    name = 'sse'

    # 指定当前spider使用特定的pipeline
    # custom_settings = {'ITEM_PIPELINES': {'ecoAlert.pipelines.DatabasePipeline': 300}}

    params = (
        # ('jsonCallBack', 'jsonpCallback62785'),
        ('searchDate', '2020-12-29'),
        ('sqlId', 'COMMON_SSE_SJ_GPSJ_CJGK_DAYCJGK_C'),
        ('stockType', '90'),
        # ('_', '1610008188021'),
    )

    # start_urls = ['http://www.cninfo.com.cn/new/hisAnnouncement/query']

    # 设置搜索关键词
    keywords = ["", "退市", "上市"]

    def start_requests(self):
        url = 'http://query.sse.com.cn/commonQuery.do'
        # 设置时间区间为今天
        # self.data["seDate"] += datetime.now().strftime("%Y-%m-%d")
        # 每个搜索条件搜一次, 拉取最新的一页
        # for kw in self.keywords:
            # self.data["searchkey"] = kw
        yield scrapy.FormRequest(url=url, callback=self.parse, method="GET", headers=headers, formdata=self.params)

    def parse(self, response):
        """解析得到的response"""
        jrsp = json.loads(response.text)
        # 将announces 列表中的每一个item单独返回
        return jrsp
