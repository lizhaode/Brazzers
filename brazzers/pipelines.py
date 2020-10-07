# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from brazzers.spiders.Starter import AllVideo
from brazzers.items import BrazzersItem


class BrazzersPipeline:
    def open_spider(self, spider: AllVideo):
        self.file = open('url.txt', 'w')

    def close_spider(self, spider: AllVideo):
        self.file.close()

    def process_item(self, item, spider: AllVideo):
        if isinstance(item, BrazzersItem):
            self.file.write(item['download_url'] + '\n')
        return item


class SaveInfoPipeline:
    def open_spider(self, spider: AllVideo):
        self.file = open('info.txt', 'w')

    def close_spider(self, spider: AllVideo):
        self.file.close()

    def process_item(self, item, spider: AllVideo):
        if isinstance(item, BrazzersItem):
            self.file.write('name: {0}\n'.format(item['title']))
            self.file.write('publish date: {0}\n'.format(item['release_date']))
            self.file.write('description: {0}\n\n\n'.format(item['desc']))
        return item
