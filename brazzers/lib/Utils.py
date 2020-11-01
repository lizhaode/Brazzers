from datetime import datetime


def extract_download_url(result: dict) -> str or None:
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


def parse_date(date: str) -> str:
    time = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
    return time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
