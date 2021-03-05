# ecoAlert工具说明

基于scrapy的一个简单爬虫项目.

初步设计目标是搜集巨潮网上的公司披露信息, 获取其中有价值的部分

1. 储存在后台数据库中
2. 将新增的, 需要通知的信息发送给kafka系统

目前已经新增对上交所数据获取的支持.

## 安装

运行环境为python3, 安装依赖库即可

```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -U pip
(venv) $ pip install -r requirements.txt
```

## 运行

```
scrapy crawl cninfo
```

其中的`cninfo`是spider的name, 会在下面章节讲到.

## 代码结构

```
├── ecoAlert
├── prototype.py
├── readme.md
├── requirements.txt
├── scrapy.cfg
└── setup.py
```

最顶层的文件都是和在各种scrapy平台部署相关的配置, 单纯的使用暂时无需考虑.

核心代码在`ecoAlert`项目文件夹中.

`items.py` 定义爬取后的结构化字段, 本项目中因为和models功能上有重叠, 暂未使用.

`middlewares.py`主要负责对网络通信做微调, 在目前并未使用.

`models.py`定义了需要储存的对象以及其数据库字段类型.

`pipelines.py`定义了后处理爬取的数据的逻辑.

`settings.py` 一些配置参数, 例如数据库的连接字符串.

`spiders` 针对不同站点的爬虫.

```
ecoAlert
├── __init__.py
├── items.py
├── middlewares.py
├── models.py
├── pipelines.py
├── settings.py
└── spiders
    ├── __init__.py
    ├── cninfo_spider.py
    ├── headers.py
    └── sse_spider.py
```

### spiders

spider文件夹中就是用来调用的各个爬虫的逻辑, 以`cninfo_spider.py`为例:

```python
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
            yield scrapy.FormRequest(url=url, callback=self.parse, method="POST", headers=MAC_HEADERS,formdata=self.data)
            
    def parse(self, response):
        """解析得到的response"""
        jrsp = json.loads(response.text)
        # 将announces 列表中的每一个item单独返回
        for i in jrsp["announcements"]:
            yield i
```

类的属性`name`就是在命令行中调用`scrapy crawl cninfo`所需要输入的name.

`custom_settings = {'ITEM_PIPELINES': {'ecoAlert.pipelines.DatabasePipeline': 300}}`会覆盖`settings.py`中的设置, 使得不同的spider可以使用不同的后处理流程.

实际上这个类被外部调用的函数就是`start_requests`, 外部调用会将其视为一个`iterator`, 取出全部的返回.

忽略其网络部分的逻辑, 这个函数返回的内容是:

```python
scrapy.FormRequest(url=url, callback=self.parse, method="POST", headers=MAC_HEADERS,formdata=self.data)
```

代表当获得对应url的返回时, 使用`self.parse`函数处理url结果后返回.

`parse`函数可以根据实际的response结构来调整, 在这里不再赘述.

### pipelines.py

pipelines文件实际上定义的是spider的返回的后处理问题, 也就是, 如何在本地分类, 清洗, 储存. 最简单的方式当然是建立一个json文件储存所有的数据, scrapy默认也提供这种方式, 但是考虑到json的查询和使用其实并不适用于长时间的生产环境, 本项目使用了database后端.

基类`BaseDBPipeline`

```python
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
```

该类封装了一些`models.py`中的函数, 并且提供了基础的一致性保证, 也即当提交出现异常时, 会通过回滚保证数据库本身的安全.

实际给`cninfo`使用的`DatabasePipeline`, (文档中的kafka模块相关代码考虑到外网保密要求仅为示例),

实际流程的入口为`process_item`函数, 其中`item`参数就是spider的返回值, 例如, 是`CninfoSpider.parse`函数的返回值. `spider`参数就是整个`CninfoSpider.parse`类.

代码中示例了如何使用`sqlalchemy`完成ORM的操作, 将数据库的CRUD转化为了对对象属性的操作.

具体流程大致为:

1. 检查数据库中是否存在标题相同点公告
2. 如果存在就更新
3. 如果不存在就新建一个, 且通过kafka接口发送出去.

```python
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
```

### models.py

定义全部的需要储存在数据库中的对象, 例如:

```
class Announcement(DeclarativeBase, ModelUpdateMixin):
    """Sqlalchemy ORM"""
    __tablename__ = "announcement"

    id = Column(Integer, primary_key=True)
    secCode = Column("secCode", String, nullable=True)
    secName = Column("secName", String, nullable=True)
    orgId = Column("orgId", String, nullable=True)
    announcementId = Column("announcementId", String, nullable=True)
    announcementTitle = Column("announcementTitle", String, nullable=True)
    announcementTime = Column("announcementTime", String, nullable=True)
    adjunctUrl = Column("adjunctUrl", String, nullable=True)
    adjunctSize = Column("adjunctSize", String, nullable=True)
    adjunctType = Column("adjunctType", String, nullable=True)
    storageTime = Column("storageTime", String, nullable=True)
    columnId = Column("columnId", String, nullable=True)
    pageColumn = Column("pageColumn", String, nullable=True)
    announcementType = Column("announcementType", String, nullable=True)
    associateAnnouncement = Column("associateAnnouncement", String, nullable=True)
    important = Column("important", String, nullable=True)
    batchNum = Column("batchNum", String, nullable=True)
    announcementContent = Column("announcementContent", String, nullable=True)
    orgName = Column("orgName", String, nullable=True)
    announcementTypeName = Column("announcementTypeName", String, nullable=True)
```

一个类对应一张表, 每个属性都对应一个数据库的列, 一个对象相当于一行.

## 如何新建一个爬虫

1. 获取需要爬取的网页的url
2. 在spiders文件夹中新建一个文件, 在其中定一个继承了`scrapy.Spider`的类, 完善其`start_requests`函数.
3. 根据获取好的数据结构, 在`models.py`中定义一个继承了`DeclarativeBase, ModelUpdateMixin`的类, 在类中定义好需要的列
4. 在`pipelines.py`中新建一个pipeline, 完善处理逻辑, 将parse返回的内容处理成在models中定义的类的结构.
5. 回到新建的spider文件中, 通过`custom_settings`来指定该spider应该使用的pipeline.
6. 测试.

