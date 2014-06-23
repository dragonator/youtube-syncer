import os

from filters import Filter
from playlist_info import PlaylistInfo
from settings import Settings


class YTSyncer():
    playlists = {}
    filtered_playlists = None
    target_directory = os.getcwd()
    filters = {}
    format_and_quality = PlaylistInfo.format_and_quality
    _status = "Idle"

    def __init__(self, url=None):
        if url is not None:
            self.load_playlists(url)
        default_settings = Settings()
        self.filters = default_settings.default_filters
        self.target_directory = default_settings.default_target_directory

    def set_status(self, message):
        self._status = message

    @property
    def status(self):
        return self._status

    def get_urls(self, url):
        if url.find('playlists') > 0:
            playlists_urls = PlaylistInfo.get_playlists_urls(url)
        else:
            playlists_urls = [url]

        return playlists_urls

    def load_playlists(self, url):
        self.set_status("Loading playlists...")

        playlists = {}
        for playlist_url in self.get_urls(url):
            playlist_info = PlaylistInfo.get_playlist_videos_info(playlist_url)
            playlists = dict(list(playlists.items()) +
                             list(playlist_info.items()))

        self.set_status("Checking available file formats and streams...")
        self.format_and_quality = \
            PlaylistInfo.get_available_formats_and_quality(playlists)
        self.playlists = playlists

    def filter_videos(self, filters):
        self.filtered_playlists = Filter.filter_all(filters, self.playlists)

    def download_videos(self):
        if self.filtered_playlists is None:
            self.filtered_playlists = self.playlists

        for playlist, videos in self.filtered_playlists.items():
            target_directory = self.target_directory + os.sep + playlist
            if not os.path.exists(target_directory) and len(videos) != 0:
                os.makedirs(target_directory)

            for video in videos:
                stream = video['selected_stream']
                self.set_status("Downloading {}...".format(stream.filename))
                file_fullpath = target_directory + os.sep + stream.filename
                stream.download(filepath=file_fullpath)
