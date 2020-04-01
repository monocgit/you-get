#!/usr/bin/env python

import json
import re

from ..common import get_content, r1, match1, playlist_not_supported
from ..extractor import VideoExtractor

__all__ = ['cntv_download', 'cntv_download_by_id']


class CNTV(VideoExtractor):
    name = 'CNTV.com'
    stream_types = [
        {'id': '1', 'video_profile': '1280x720_2000kb/s', 'map_to': 'chapters4'},
        {'id': '2', 'video_profile': '1280x720_1200kb/s', 'map_to': 'chapters3'},
        {'id': '3', 'video_profile': '640x360_850kb/s', 'map_to': 'chapters2'},
        {'id': '4', 'video_profile': '480x270_450kb/s', 'map_to': 'chapters'},
        {'id': '5', 'video_profile': '320x180_200kb/s', 'map_to': 'lowChapters'},
    ]

    ep = 'http://vdn.apps.cntv.cn/api/getIpadVideoInfo.do?pid={}'

    def __init__(self):
        super().__init__()
        self.api_data = None

    def prepare(self, **kwargs):
        self.api_data = json.loads(get_content(self.__class__.ep.format(self.vid)))
        self.title = self.api_data['title']
        for s in self.api_data['video']:
            for st in self.__class__.stream_types:
                if st['map_to'] == s:
                    urls = self.api_data['video'][s]
                    src = [u['url'] for u in urls]
                    stream_data = dict(src=src, size=0, container='mp4', video_profile=st['video_profile'])
                    self.streams[st['id']] = stream_data


def cntv_download_by_id(rid, **kwargs):
    if type(rid) is list:
        for e in rid:
            CNTV().download_by_vid(e, **kwargs)
    else:
        CNTV().download_by_vid(rid, **kwargs)


def cntv_download(url, **kwargs):
    if re.match(r'http://tv\.cntv\.cn/video/(\w+)/(\w+)', url):
        rid = match1(url, r'http://tv\.cntv\.cn/video/\w+/(\w+)')
    elif re.match(r'http://tv\.cctv\.com/\d+/\d+/\d+/\w+.shtml', url):
        rid = r1(r'var guid = "(\w+)"', get_content(url))
    elif re.match(r'http://\w+\.cntv\.cn/(\w+/\w+/(classpage/video/)?)?\d+/\d+\.shtml', url) or \
         re.match(r'http://\w+.cntv.cn/(\w+/)*VIDE\d+.shtml', url) or \
         re.match(r'http://(\w+).cntv.cn/(\w+)/classpage/video/(\d+)/(\d+).shtml', url) or \
         re.match(r'http://\w+.cctv.com/\d+/\d+/\d+/\w+.shtml', url) or \
         re.match(r'http://\w+.cntv.cn/\d+/\d+/\d+/\w+.shtml', url):
        page = get_content(url)
        rid = r1(r'videoCenterId","(\w+)"', page)
        if rid is None:
            guid = re.search(r'guid\s*=\s*"([0-9a-z]+)"', page).group(1)
            rid = guid
    elif re.match(r'http://ncpa-classic\.cntv\.cn/\d+/\d+/\d+/VIDE\w+.shtml', url):
        page = get_content(url)
        rid = r1(r"initMyAray=\s'(\w+)'", page)
        if rid is None:
            myararrys = re.search(r"myararrys\s*=\s*\[\n'([0-9a-z]+)'", page).group(1)
            rid = myararrys
    elif re.match(r'http://ncpa-classic\.cntv\.cn/\d+/\d+/\d+/VIDA\w+.shtml', url):
        page = get_content(url)
        rid = re.findall(r'"(\w{32})"', page)

         #initMyAray=    'edd9109e6fb94dd38590bb1356906c6b';

         # var myararrys = [
                 #       'edd9109e6fb94dd38590bb1356906c6b'
                 #               ];

         # var myararrys = [
                 #       '42f658bf39634ec2be2f578ce7023c5e','09e341a7aee64c0e86f2857ece459467','c34e614f83c24667874837363799ed20',             'ce4bd8afdd514733bae08249dc60e2b0','ef11ac0fa60e436e9483b2fe8cabb668','23c02ca2204849d6a18605f5ddc2eefb','28634cac4b8540fb8372791cbe2ae6e4',  '4d026915dbf2490cb84b9babd095e606','bb78bd10b5224122a180245a0c80f111'
                 #               ];

    elif re.match(r'http://xiyou.cntv.cn/v-[\w-]+\.html', url):
        rid = r1(r'http://xiyou.cntv.cn/v-([\w-]+)\.html', url)
    else:
        raise NotImplementedError(url)

    CNTV().download_by_vid(rid, **kwargs)

site_info = "CNTV.com"
download = cntv_download
download_playlist = playlist_not_supported('cntv')
