from datetime import datetime

import scrapy
from scrapy.http.response.html import HtmlResponse

from brazzers.items import BrazzersItem


class BaseSpider(scrapy.Spider):
    name = 'all'

    def start_requests(self):
        which = self.settings.get('WHICH_ENABLE')
        if which == 'tag':
            tag_id = self.settings.get('TAG_ID')
            base_url = 'https://site-api.project1service.com/v2/releases?limit=96&offset=0&type=scene&orderBy' \
                       '=-dateReleased&tagId={0}'.format(tag_id)
        elif which == 'date':
            start_date = self.settings.get('START_DATE')
            end_date = self.settings.get('END_DATE')
            base_url = 'https://site-api.project1service.com/v2/releases?dateReleased=>{0},' \
                       '<{1}&limit=96&offset=0&type=scene&orderBy=-dateReleased&type=scene'.format(start_date, end_date)
        else:
            collection_id = self.settings.get('COLLECTION_ID')
            base_url = 'https://site-api.project1service.com/v2/releases?limit=96&offset=0&type=scene&orderBy' \
                       '=-dateReleased&collectionId={0}'.format(collection_id)

        yield scrapy.Request(url=base_url)

    def parse(self, response: HtmlResponse, **kwargs):
        total = response.json().get('meta').get('total')
        self.logger.warn('videos count: %s', total)
        count = response.json().get('meta').get('count')
        if count != 0:
            old_offset = int(response.url.split('offset=')[1].split('&')[0])
            offset = 96 + int(response.url.split('offset=')[1].split('&')[0])
            base_url = response.url.replace('offset={0}'.format(old_offset), 'offset={0}')
            yield scrapy.Request(url=base_url.format(offset))

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

    def extract_download_url(self, result: dict) -> str or None:
        # 有的视频没有提供播放地址, 是一个 []
        video_info = result.get('videos')
        if len(video_info) != 0:
            files = video_info.get('full').get('files')
            if files.get('2160p') is not None:
                return files.get('2160p').get('urls').get('download')
            if files.get('1080p') is not None:
                return files.get('1080p').get('urls').get('download')
            if files.get('720p') is not None:
                return files.get('720p').get('urls').get('download')
            return None

    def parse_date(self, date: str) -> str:
        time = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        return time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
