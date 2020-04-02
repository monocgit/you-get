#!/usr/bin/env python

import json
import re

from ..common import get_content, content_to_json, r1, match1, playlist_not_supported
from ..extractor import VideoExtractor

__all__ = ['ncpa_download', 'ncpa_download_by_id']


class NCPA(VideoExtractor):
    name = 'NCPA-CLASSIC.cntv.com'
    stream_types = [
        {'id': '1', 'video_profile': '1280x720_2000kb/s', 'map_to': 'chapters4'},
        {'id': '2', 'video_profile': '1280x720_1200kb/s', 'map_to': 'chapters3'},
        {'id': '3', 'video_profile': '640x360_850kb/s', 'map_to': 'chapters2'},
        {'id': '4', 'video_profile': '480x270_450kb/s 192kb/s', 'map_to': 'chapters'},
        {'id': '5', 'video_profile': '320x180_200kb/s 128kb/s', 'map_to': 'lowChapters'},
    ]

    ep = 'http://vdn.apps.cntv.cn/api/getIpadVideoInfo.do?pid={}'

    def __init__(self):
        super().__init__()
        self.api_data = None

    def prepare(self, **kwargs):
        self.api_data = content_to_json(get_content(self.__class__.ep.format(self.vid)))
        self.title = self.api_data['title']
        for s in self.api_data['video']:
            for st in self.__class__.stream_types:
                if st['map_to'] == s:
                    urls = self.api_data['video'][s]
                    src = [u['url'] for u in urls]
                    stream_data = dict(src=src, size=0, container='mp4', video_profile=st['video_profile'])
                    self.streams[st['id']] = stream_data


def ncpa_download_by_id(rid, **kwargs):
    if type(rid) is list:
        for e in rid:
            NCPA().download_by_vid(e, **kwargs)
    else:
        NCPA().download_by_vid(rid, **kwargs)


def ncpa_download(url, **kwargs):
    if re.match(r'http://ncpa-classic\.cntv\.cn/\d+/\d+/\d+/VIDE\w+.shtml', url):
        page = get_content(url)
        rid = r1(r"initMyAray=\s'(\w+)'", page)
        if rid is None:
            myararrys = re.search(r"myararrys\s*=\s*\[\n'([0-9a-z]+)'", page).group(1)
            rid = myararrys
    elif re.match(r'http://ncpa-classic\.cntv\.cn/\d+/\d+/\d+/VIDA\w+.shtml', url):
        page = get_content(url)
        rid = re.findall(r'"(\w{32})"', page)
    else:
        raise NotImplementedError(url)

    ncpa_download_by_id(rid, **kwargs)

site_info = "ncpa-claasic.cntv.com"
download = ncpa_download
download_playlist = playlist_not_supported('ncpa')
