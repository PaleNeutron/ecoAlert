#   This file is part of the ecoAlert project.
#   Copyright (c) 2020 John Lyu
#   All Rights Reserved.
#   Unauthorized copying of this file, via any medium is strictly prohibited
#   Proprietary and confidential

# usage:
#
# You need to create two files: one for service, other for timer with same name.
#
# example:
#
# /etc/systemd/system/ecoAlert.service
#
# ```
# [Unit]
# Description=ecoAlert job
#
# [Service]
# Type=oneshot
# ExecStart=python3 {full path of this script}
# ```
#
# /etc/systemd/system/ecoAlert.timer
#
# ```
# [Unit]
# Description=ecoAlert
#
# [Timer]
# OnUnitActiveSec=60s
# OnBootSec=60s
#
# [Install]
# WantedBy=timers.target
# ```
#
# after that reload the systemd using command `systemctl daemon-reload` and start your timer by
# `systemctl start ecoAlert.timer`, or enable it by default `systemctl enable ecoAlert.timer`.


import requests
from datetime import datetime

# cookies are not necessary
# cookies = {
#     'JSESSIONID': 'ACC0D173E769850EFB0F366B6B48F6D2',
#     'insert_cookie': '37836164',
#     'routeId': '.uc2',
#     '_sp_ses.2141': '*',
#     '_sp_id.2141': 'd79ad74e-470a-4e21-b68b-96ee1b986383.1609297961.1.1609298002.1609297961.9a973c38-389f-4bef-bc9b-905af4af0568',
# }

headers = {
    'Proxy-Connection': 'keep-alive',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'http://www.cninfo.com.cn',
    'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
}
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
    'seDate': '2020-06-30~' + datetime.now().strftime("%Y-%m-%d"),
    'sortName': '',
    'sortType': '',
    'isHLtitle': 'true'
}


class Backend(object):
    """Backend for this monitor or watchdog
    provide 3 features
    1. save
    2. load
    3. check if similar item exists
    note: sometimes a alert will appear multiple times with different title, in this case, should be treated as same.
    """

    def __init__(self):
        """Constructor for Backend"""
        # storage could be a dict, a file or a redis/sqlite/MySQL database
        self.storage = {}

    def save(self, item, detail="."):
        self.storage[item] = detail

    def load(self, item_key):
        try:
            return self.storage[item_key]
        except KeyError:
            return None

    def match_rule(self, item_key, item_to_match):
        """should implement later, check if they are matched"""
        return item_key in item_to_match

    def has_similar(self, item):
        keys = self.storage.keys()
        return any([self.match_rule(item, i) for i in keys])


def should_alert(item_name):
    return True


def alert(item_name):
    pass


def main():
    # response["announcements"] 格式样例
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

    # 配置
    data["searchkey"] = "退市"
    backend = Backend()

    # 抓取
    response = requests.post('http://www.cninfo.com.cn/new/hisAnnouncement/query', headers=headers, data=data,
                             verify=False)
    j = response.json()

    # 获取关键词
    for ji in j["announcements"]:
        item_key = ji["announcementTitle"]

        # 如果从未发送过 且 应当报警 则 报警
        if not backend.has_similar(item_key) and should_alert(item_key):
            alert(item_key)

        # 记录到后台数据库中
        backend.save(item_key, ji["adjunctUrl"])

        print(ji)


if __name__ == '__main__':
    main()
