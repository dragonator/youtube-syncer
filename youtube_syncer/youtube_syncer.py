import sys
import re
import urllib.request

import pafy
from bs4 import BeautifulSoup


class YTSyncer():
    playlists = dict()

    def __init__(self, url=None):
        if url:
            self.playlists = YTSyncer.load_playlists(url)
        else:
            self.playlists = dict()

    @staticmethod
    def _to_int(string):
        return int(re.sub(r'[^0-9]', '', string))

    @staticmethod
    def _get_filtered_video_info(pafy_playlist_item):
        # This will tell us at return if there is any problem
        # with filtering video information
        succeeded = True

        try:
            meta_info = pafy_playlist_item['playlist_meta']
            video_info =\
                dict(title=meta_info['title'],
                     likes=meta_info['likes'],
                     dislikes=meta_info['dislikes'],
                     views=YTSyncer._to_int(meta_info['views']),
                     upload_time=meta_info['added'],
                     comments_count=YTSyncer._to_int(meta_info['comments']),
                     length_seconds=meta_info['length_seconds'],
                     rating=meta_info['rating'],
                     streams=pafy_playlist_item['pafy'].allstreams,
                     for_download=pafy_playlist_item['pafy'].getbest())

        except IOError as message:
            title = '[ '+pafy_playlist_item['playlist_meta']['title']+' ]'
            message = re.sub(r'\[.+\]', title, str(message))
            print(message)
            succeeded = False

        except:
            print(sys.exc_info()[0])
            succeeded = False

        return video_info, succeeded

    @staticmethod
    def get_playlists_urls(url_to_playlists_page):
        page_content = urllib.request.urlopen(url_to_playlists_page).read()
        soup_obj = BeautifulSoup(page_content)
        playlists_urls = list()
        for h3_tag in soup_obj.findAll('h3', {'class': 'yt-lockup-title'}):
            for a_tag in h3_tag.findAll('a', {'class': 'yt-uix-tile-link'}):
                playlists_urls.append('https://www.youtube.com'+a_tag['href'])

        return playlists_urls

    @staticmethod
    def get_playlist_videos_info(url_to_playlist_page):
        playlists = dict()

        # Get playlist information using pafy module
        pafy_playlist_info = pafy.get_playlist(url_to_playlist_page)

        # Get playlist title
        playlist_title = pafy_playlist_info['title']

        # Creating list for the videos in a playlist
        # and fill it
        playlists[playlist_title] = list()
        for video in pafy_playlist_info['items']:
            video_info, succeeded = YTSyncer._get_filtered_video_info(video)
            if succeeded:
                playlists[playlist_title].append(video_info)

        return playlists

    @staticmethod
    def load_playlists(url):
        # Dictionary with (all playlists/the playlist) information
        playlists = dict()
        if url.find('playlists') > 0:
            playlists_urls = YTSyncer.get_playlists_urls(url)
            for playlist_url in playlists_urls:
                playlist_info = YTSyncer.get_playlist_videos_info(playlist_url)
                playlists = \
                    dict(list(playlists.items()) + list(playlist_info.items()))

        else:  # if url.find('playlist') > 0:
            playlists = YTSyncer.get_playlist_videos_info(url)

        return playlists
