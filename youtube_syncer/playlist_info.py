import re
import sys
import urllib

import pafy
from bs4 import BeautifulSoup


class PlaylistInfo():
    format_and_quality = {
        "normal": set(),
        "video": set(),
        "audio": set()
    }
    domain_name = 'https://www.youtube.com'

    @classmethod
    def _to_int(cls, string):
        return int(re.sub(r'[^0-9]', '', string))

    @classmethod
    def get_available_formats_and_quality(cls, playlists):
        format_and_quality = cls.format_and_quality
        for videos in playlists.values():
            for video in videos:
                for stream in video['streams'].allstreams:
                    _format, _quality = str(stream).split(":")
                    format_and_quality[_format].add(_quality)

        for key in format_and_quality.keys():
            format_and_quality[key] = list(format_and_quality[key])
            format_and_quality[key].sort()

        return format_and_quality

    @classmethod
    def _get_filtered_video_info(cls, video):
        try:
            meta_info = video['playlist_meta']
            video_info = {
                "title": meta_info['title'],
                "likes": meta_info['likes'],
                "dislikes": meta_info['dislikes'],
                "views": cls._to_int(meta_info['views']),
                "upload_date": meta_info['added'],
                "comments_count": cls._to_int(meta_info['comments']),
                "length_seconds": meta_info['length_seconds'],
                "rating": meta_info['rating'],
                "streams": video['pafy'],
                "selected_stream": None
            }
        except:
            raise

        return video_info

    @classmethod
    def get_playlists_urls(cls, url_to_playlists_page):
        page_content = urllib.request.urlopen(url_to_playlists_page).read()
        soup_obj = BeautifulSoup(page_content)
        playlists_urls = []
        for h3_tag in soup_obj.findAll('h3', {'class': 'yt-lockup-title'}):
            for a_tag in h3_tag.findAll('a', {'class': 'yt-uix-tile-link'}):
                playlists_urls.append(cls.domain_name+a_tag['href'])

        return playlists_urls

    @classmethod
    def get_playlist_videos_info(cls, url_to_playlist_page):
        playlists = {}

        pafy_playlist_info = pafy.get_playlist(url_to_playlist_page)
        playlist_title = pafy_playlist_info['title']

        playlists[playlist_title] = []
        for video in pafy_playlist_info['items']:
            try:
                video_info = cls._get_filtered_video_info(video)
                playlists[playlist_title].append(video_info)

            except IOError as message:
                title = '[ ' + video["playlist_meta"]["title"] + ' ]'
                message = re.sub(r'\[.+\]', title, str(message))
                print(message)

            except:
                print(sys.exc_info()[0])

        return playlists
