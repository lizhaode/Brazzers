import math

import scrapy
from scrapy.http.response.html import HtmlResponse

from brazzers.items import BrazzersItem
from brazzers.lib.Utils import parse_date, extract_download_url


class AllVideo(scrapy.Spider):
    name = 'collection'

    def start_requests(self):
        collection_id = self.settings.get('COLLECTION_ID')
        self.base_url = '''https://site-api.project1service.com/v2/releases?
        limit=96&offset=0&orderBy=-dateReleased&collectionId={0}'''.format(collection_id)
        yield scrapy.Request(url=self.base_url)

    def parse(self, response: HtmlResponse, **kwargs):
        total = response.json().get('meta').get('total')
        base_url = self.base_url.replace('offset=0', 'offset={0}')
        round_number = math.floor(total / 96)
        for i in range(round_number):
            # 根据总的视频条数 计算 offset 的值
            offset = 96 * (i + 1)
            yield scrapy.Request(url=base_url.format(offset), callback=self.offset_parse)

        # 想要的结果数据都在 result 中, 他是一个 list
        for result in response.json().get('result'):  # type:dict
            title = result.get('title')
            release_date = parse_date(result.get('dateReleased'))
            desc = result.get('description')
            download_url = extract_download_url(result)
            if download_url is not None:
                yield BrazzersItem(title=title, release_date=release_date, desc=desc, download_url=download_url)
            else:
                self.logger.warn('no download,the video name: %s', title)

    def offset_parse(self, response: HtmlResponse, **kwargs):
        for result in response.json().get('result'):  # type:dict
            title = result.get('title')
            release_date = parse_date(result.get('dateReleased'))
            desc = result.get('description')
            download_url = extract_download_url(result)
            if download_url is not None:
                yield BrazzersItem(title=title, release_date=release_date, desc=desc, download_url=download_url)
            else:
                self.logger.warn('no download,the video name: %s', title)
