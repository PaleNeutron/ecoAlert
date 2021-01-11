#   This file is part of the ecoAlert project.
#   Copyright (c) 2020 John Lyu
#   All Rights Reserved.
#   Unauthorized copying of this file, via any medium is strictly prohibited
#   Proprietary and confidential

import json
from datetime import datetime
from .headers import MAC_HEADERS

import scrapy


# data字段说明
#
# data = {
#     'pageNum': '1',
#     'pageSize': '30',
#     'column': 'szse',
#     'tabName': 'fulltext',
#     'plate': 'sz;szmb;szzx;szcy;sh;shmb;shkcp',  # 深市; 深主板; 深中小板; 创业板; 沪市; 沪主板; 科创板
#     'stock': '600886,gssh0600886',  # 股票编号
#     'searchkey': '退市',  # 关键词
#     'secid': '',  # 未知
#     # 年报, 半年报, 一季报, 三季报, 业绩预告, 权益分派, 董事会
#     'category': 'category_ndbg_szsh;category_bndbg_szsh;category_yjdbg_szsh;category_sjdbg_szsh;category_yjygjxz_szsh;category_qyfpxzcs_szsh;category_dshgg_szsh',
#     'trade': '电力、热力、燃气及水生产和供应业;农、林、牧、;交通运输、仓储和邮政业',  # 行业
#     'seDate': '2020-06-30~2020-12-31',  # 时间区间
#     'sortName': 'time',  # 排序列名
#     'sortType': 'desc',  # 排序方向
#     'isHLtitle': 'true'
# }
#

# response["announcements"][0] 格式样例
# {
#     "id": null,
#     "secCode": "000927",
#     "secName": "*ST\u590f\u5229",
#     "orgId": "gssz0000927",
#     "announcementId": "1208981224",
#     "announcementTitle": "\u7acb\u4fe1\u4f1a\u8ba1\u5e08\u4e8b\u52a1\u6240\uff08\u7279\u6b8a\u666e\u901a\u5408\u4f19\uff09\u5173\u4e8e\u516c\u53f8\u7533\u8bf7\u64a4\u9500\u516c\u53f8\u80a1\u7968<em>\u9000\u5e02</em>\u98ce\u9669\u8b66\u793a\u4e2d\u6709\u5173\u8d22\u52a1\u4e8b\u9879\u7684\u8bf4\u660e",
#     "announcementTime": 1608825600000,
#     "adjunctUrl": "finalpage/2020-12-25/1208981224.PDF",
#     "adjunctSize": 2916,
#     "adjunctType": "PDF",
#     "storageTime": null,
#     "columnId": "09020202||250101||251302",
#     "pageColumn": "SZZB",
#     "announcementType": "01010903||010112||0129",
#     "associateAnnouncement": null,
#     "important": null,
#     "batchNum": null,
#     "announcementContent": "",
#     "orgName": null,
#     "announcementTypeName": null
# },


class CninfoSpider(scrapy.Spider):
    name = 'cninfo'

    # 指定当前spider使用特定的pipeline
    custom_settings = {'ITEM_PIPELINES': {'ecoAlert.pipelines.DatabasePipeline': 300}}

    data = {
        'pageNum': '1',
        'pageSize': '30',
        'column': 'szse',
        'tabName': 'fulltext',
        'plate': '',
        'stock': '',
        'searchkey': '',
        'secid': '',
        'category': '',
        'trade': '',
        'seDate': '2020-06-30~',  # '2020-06-30~' + datetime.now().strftime("%Y-%m-%d"),
        'sortName': '',
        'sortType': '',
        'isHLtitle': 'true'
    }

    # start_urls = ['http://www.cninfo.com.cn/new/hisAnnouncement/query']

    # 设置搜索关键词
    keywords = ["", "退市", "上市"]

    def start_requests(self):
        url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        # 注意, 出现在结果标题中的关键词会被<em>标签包围, 请考虑是否要处理掉
        # 设置时间区间为今天
        self.data["seDate"] += datetime.now().strftime("%Y-%m-%d")
        # 每个搜索条件搜一次, 拉取最新的一页
        for kw in self.keywords:
            self.data["searchkey"] = kw
            yield scrapy.FormRequest(url=url, callback=self.parse, method="POST", headers=MAC_HEADERS,
                                     formdata=self.data)

    def parse(self, response):
        """解析得到的response"""
        jrsp = json.loads(response.text)
        # 将announces 列表中的每一个item单独返回
        for i in jrsp["announcements"]:
            yield i
