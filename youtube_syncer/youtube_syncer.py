import sys
import os
import re
import urllib.request

import pafy

from filters import Filter
from playlist_info import PlaylistInfo


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
    format_and_quality = PlaylistInfo.format_and_quality

    def __init__(self, url=None):
        if url is not None:
            self.load_playlists(url)

    def load_playlists(self, url):
        playlists = {}
        if url.find('playlists') > 0:
            playlists_urls = PlaylistInfo.get_playlists_urls(url)
        else:
            playlists_urls = [url]

        for playlist_url in playlists_urls:
            playlist_info = PlaylistInfo.get_playlist_videos_info(playlist_url)
            playlists = \
                dict(list(playlists.items()) + list(playlist_info.items()))

        self.format_and_quality = \
            PlaylistInfo._get_available_formats_and_quality(playlists)
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
