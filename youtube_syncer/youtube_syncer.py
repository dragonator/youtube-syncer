import sys
import os
import re
import urllib.request

import pafy
from bs4 import BeautifulSoup

from filters import Filter


class YTSyncer():
    playlists = {}
    filtered_playlists = {}
    target_directory = os.getcwd()
    filters = {
        "selected": None,
        "min_likes": None,
        "max_likes": None,
        "min_length_in_minutes": None,
        "max_length_in_minutes": None,
        "min_views_count": None,
        "max_views_count": None,
        "likes_dislikes_difference": None,
        "min_comments_count": None,
        "max_comments_count": None,
        "before_date": None,
        "after_date": None,
        "stream_format": None,
        "stream_quality": None
    }
    format_and_quality = {
        "normal": [],
        "video": [],
        "audio": []
    }

    def __init__(self, url=None):
        if url is not None:
            self.load_playlists(url)

    def _to_int(self, string):
        return int(re.sub(r'[^0-9]', '', string))

    def _get_available_format_and_quality(self, playlists):
        for videos in playlists.values():
            for video in videos:
                for stream in video['streams'].allstreams:
                    _format, _quality = str(stream).split(":")
                    if _quality not in self.format_and_quality[_format]:
                        self.format_and_quality[_format].append(_quality)

        for streams in self.format_and_quality.values():
            streams.sort()

    def _get_filtered_video_info(self, video):
        try:
            meta_info = video['playlist_meta']
            video_info = {
                "title": meta_info['title'],
                "likes": meta_info['likes'],
                "dislikes": meta_info['dislikes'],
                "views": self._to_int(meta_info['views']),
                "upload_date": meta_info['added'],
                "comments_count": self._to_int(meta_info['comments']),
                "length_seconds": meta_info['length_seconds'],
                "rating": meta_info['rating'],
                "streams": video['pafy'],
                "selected_stream": None
            }
        except:
            raise

        return video_info

    def get_playlists_urls(self, url_to_playlists_page):
        page_content = urllib.request.urlopen(url_to_playlists_page).read()
        soup_obj = BeautifulSoup(page_content)
        playlists_urls = []
        domain_name = 'https://www.youtube.com'
        for h3_tag in soup_obj.findAll('h3', {'class': 'yt-lockup-title'}):
            for a_tag in h3_tag.findAll('a', {'class': 'yt-uix-tile-link'}):
                playlists_urls.append(domain_name+a_tag['href'])

        return playlists_urls

    def get_playlist_videos_info(self, url_to_playlist_page):
        playlists = {}

        pafy_playlist_info = pafy.get_playlist(url_to_playlist_page)
        playlist_title = pafy_playlist_info['title']

        playlists[playlist_title] = []
        for video in pafy_playlist_info['items']:
            try:
                video_info = self._get_filtered_video_info(video)
                playlists[playlist_title].append(video_info)

            except IOError as message:
                title = '[ ' + video["playlist_meta"]["title"] + ' ]'
                message = re.sub(r'\[.+\]', title, str(message))
                print(message)

            except:
                print(sys.exc_info()[0])

        return playlists

    def load_playlists(self, url):
        playlists = {}
        if url.find('playlists') > 0:
            playlists_urls = self.get_playlists_urls(url)
        else:
            playlists_urls = [url]

        for playlist_url in playlists_urls:
            playlist_info = self.get_playlist_videos_info(playlist_url)
            playlists = \
                dict(list(playlists.items()) + list(playlist_info.items()))

        self._get_available_format_and_quality(playlists)
        self.playlists = playlists

    def filter_videos(self, selected=None, min_likes=None, max_likes=None,
                      min_length_in_minutes=None, max_length_in_minutes=None,
                      min_views_count=None, max_views_count=None,
                      likes_dislikes_difference=None,
                      min_comments_count=None, max_comments_count=None,
                      before_date=None, after_date=None,
                      stream_format=None, stream_quality=None):

        self.filtered_playlists = self.playlists

        if selected is not None:
            self.filtered_playlists = \
                Filter.filter_selected(selected, self.filtered_playlists)

        if min_likes is not None:
            self.filtered_playlists = \
                Filter.by_min_likes(min_likes, self.filtered_playlists)

        if max_likes is not None:
            self.filtered_playlists = \
                Filter.by_max_likes(max_likes, self.filtered_playlists)

        if min_length_in_minutes is not None:
            self.filtered_playlists = \
                Filter.by_min_length_in_minutes(min_length_in_minutes,
                                                self.filtered_playlists)

        if max_length_in_minutes is not None:
            self.filtered_playlists = \
                Filter.by_max_length_in_minutes(max_length_in_minutes,
                                                self.filtered_playlists)

        if min_views_count is not None:
            self.filtered_playlists = \
                Filter.by_min_views_count(min_views_count,
                                          self.filtered_playlists)

        if max_views_count is not None:
            self.filtered_playlists = \
                Filter.by_max_views_count(max_views_count,
                                          self.filtered_playlists)

        if likes_dislikes_difference is not None:
            self.filtered_playlists = \
                Filter.by_more_likes_than_dislikes(likes_dislikes_difference,
                                                   self.filtered_playlists)

        if min_comments_count is not None:
            self.filtered_playlists = \
                Filter.by_min_comments_count(min_comments_count,
                                             self.filtered_playlists)

        if max_comments_count is not None:
            self.filtered_playlists = \
                Filter.by_max_comments_count(max_comments_count,
                                             self.filtered_playlists)

        if before_date is not None:
            self.filtered_playlists = \
                Filter.by_before_date(before_date, self.filtered_playlists)

        if after_date is not None:
            self.filtered_playlists = \
                Filter.by_after_date(after_date, self.filtered_playlists)

        if stream_format is not None:
            self.filtered_playlists = \
                Filter.by_format_and_quality(stream_format, stream_quality,
                                             self.filtered_playlists)

    def download_videos(self):
        for playlist, videos in self.filtered_playlists.items():
            target_directory = self.target_directory + os.sep + playlist
            if not os.path.exists(target_directory) and len(videos) != 0:
                os.makedirs(target_directory)

            for video in videos:
                stream = video['selected_stream']
                file_fullpath = target_directory + os.sep + stream.filename
                stream.download(filepath=file_fullpath)
