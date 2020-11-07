# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import requests
import time

from brazzers.items import BrazzersItem
from brazzers.lib.download_header import random_other_headers
from brazzers.spiders.Base import BaseSpider


class BrazzersPipeline:
    def open_spider(self, spider: BaseSpider):
        self.file = open('url.txt', 'w')

    def close_spider(self, spider: BaseSpider):
        self.file.close()

    def process_item(self, item, spider: BaseSpider):
        if isinstance(item, BrazzersItem):
            self.file.write(item['download_url'] + '\n')
        return item


class SaveInfoPipeline:
    def open_spider(self, spider: BaseSpider):
        self.file = open('info.txt', 'w')

    def close_spider(self, spider: BaseSpider):
        self.file.close()

    def process_item(self, item, spider: BaseSpider):
        if isinstance(item, BrazzersItem):
            self.file.write('name: {0}\n'.format(item['title']))
            self.file.write('publish date: {0}\n'.format(item['release_date']))
            self.file.write('description: {0}\n\n\n'.format(item['desc']))
        return item


class DownloadPipeline:
    def process_item(self, item, spider: BaseSpider):
        base_url = 'http://127.0.0.1:8900/jsonrpc'
        token = 'token:' + spider.settings.get('ARIA_TOKEN')
        if isinstance(item, BrazzersItem):
            download_data = {
                'jsonrpc': '2.0',
                'method': 'aria2.addUri',
                'id': '0',
                'params': [token, [item['download_url']],
                           {'out': item['title'] + '.mp4', "header": random_other_headers()}]
            }
            requests.post(url=base_url, json=download_data)
        return item
