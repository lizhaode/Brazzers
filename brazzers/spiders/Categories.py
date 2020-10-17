import datetime
import math

import scrapy
from scrapy.http.response.html import HtmlResponse

from brazzers.items import BrazzersItem


class AllVideo(scrapy.Spider):
    name = 'tag'

    def start_requests(self):
        tag_id = self.settings.get('TAG_ID')
        self.base_url = '''https://site-api.project1service.com/v2/releases?
        limit=96&offset=0&orderBy=-dateReleased&tagId={0}'''.format(tag_id)
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
            release_date = self.parse_date(result.get('dateReleased'))
            desc = result.get('description')
            download_url = self.extract_download_url(result)
            if download_url is not None:
                yield BrazzersItem(title=title, release_date=release_date, desc=desc, download_url=download_url)
            else:
                self.logger.warn('no download,the video name: %s', title)

    def offset_parse(self, response: HtmlResponse, **kwargs):
        for result in response.json().get('result'):  # type:dict
            title = result.get('title')
            release_date = self.parse_date(result.get('dateReleased'))
            desc = result.get('description')
            download_url = self.extract_download_url(result)
            if download_url is not None:
                yield BrazzersItem(title=title, release_date=release_date, desc=desc, download_url=download_url)
            else:
                self.logger.warn('no download,the video name: %s', title)

    def extract_download_url(self, result: dict) -> str or None:
        # 有的视频没有提供播放地址, 是一个 []
        video_info = result.get('videos')
        if len(video_info) != 0:
            files = video_info.get('full').get('files')
            if files.get('1080p') is None:
                if files.get('720p') is None:
                    return None
                else:
                    return files.get('720p').get('urls').get('download')
            else:
                return files.get('1080p').get('urls').get('download')

    def parse_date(self, date: str) -> str:
        time = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        return time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
