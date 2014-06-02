import sys
import os
import re
import urllib.request

import pafy
from bs4 import BeautifulSoup


class YTSyncer():
    playlists = dict()
    download_here = os.getcwd()

    def __init__(self, url=None):
        if url:
            self.playlists = YTSyncer.load_playlists(url)
        else:
            self.playlists = dict()

    def _to_int(string):
        return int(re.sub(r'[^0-9]', '', string))

    def _get_filtered_video_info(pafy_playlist_item):
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
                     all_streams=pafy_playlist_item['pafy'].allstreams,
                     selected_stream=pafy_playlist_item['pafy'].getbestaudio(),
                     is_for_download=True)

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

        pafy_playlist_info = pafy.get_playlist(url_to_playlist_page)

        playlist_title = pafy_playlist_info['title']

        playlists[playlist_title] = list()
        for video in pafy_playlist_info['items']:
            video_info, succeeded = YTSyncer._get_filtered_video_info(video)
            if succeeded:
                playlists[playlist_title].append(video_info)

        return playlists

    @staticmethod
    def load_playlists(url):
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

    def download_videos(self):
        for playlist, videos in self.playlists.items():
            new_directory = self.download_here + '/' + playlist
            if not os.path.exists(new_directory):
                os.makedirs(new_directory)

            for video in videos:
                if video['is_for_download']:
                    stream = video['selected_stream']
                    file_fullpath = new_directory + '/'\
                        + stream.title + '.' + stream.extension
                    stream.download(filepath=file_fullpath)
