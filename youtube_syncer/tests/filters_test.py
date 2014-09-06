import unittest
import sys
import os
from mock import patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(os.path.dirname(os.path.abspath(__file__)))

from pafy import Pafy
from ..playlist_info import PlaylistInfo
from ..filters import Filter


url = 'www.youtube.com/playlist?list=PLKxmIVeZ2xNuJ7qBUDhOCVWzKDdJ6dPLp'
playlists = PlaylistInfo.get_playlist_videos_info(url)

class FiltersTester(unittest.TestCase):

    def setUp(self):
        self.playlists = playlists

    def test_min_likes_filter(self):
        video = {'likes': 100}
        result = Filter.has_min_likes(50, video)
        self.assertTrue(result)
        result = Filter.has_min_likes(150, video)
        self.assertFalse(result)
        result = Filter.has_min_likes(None, video)
        self.assertTrue(result)

    def test_max_likes_filter(self):
        video = {'likes': 100}
        result = Filter.has_under_max_likes(150, video)
        self.assertTrue(result)
        result = Filter.has_under_max_likes(50, video)
        self.assertFalse(result)
        result = Filter.has_under_max_likes(None, video)
        self.assertTrue(result)

    def test_min_length_filter(self):
        video = {'length_seconds': 100}
        result = Filter.has_min_length(1, video)
        self.assertTrue(result)
        result = Filter.has_min_length(2, video)
        self.assertFalse(result)
        result = Filter.has_min_length(None, video)
        self.assertTrue(result)

    def test_max_length_filter(self):
        video = {'length_seconds': 100}
        result = Filter.has_under_max_length(2, video)
        self.assertTrue(result)
        result = Filter.has_under_max_length(1, video)
        self.assertFalse(result)
        result = Filter.has_under_max_length(None, video)
        self.assertTrue(result)

    def test_min_views(self):
        video = {'views': 100}
        result = Filter.has_min_views(50, video)
        self.assertTrue(result)
        result = Filter.has_min_views(120, video)
        self.assertFalse(result)
        result = Filter.has_min_views(None, video)
        self.assertTrue(result)

    def test_max_views(self):
        video = {'views': 100}
        result = Filter.has_under_max_views(200, video)
        self.assertTrue(result)
        result = Filter.has_under_max_views(50, video)
        self.assertFalse(result)
        result = Filter.has_under_max_views(None, video)
        self.assertTrue(result)

    def test_likes_dislikes_diff(self):
        video = {'likes': 100, 'dislikes': 50}
        result = Filter.has_more_likes(30, video)
        self.assertTrue(result)
        result = Filter.has_more_likes(60, video)
        self.assertFalse(result)
        result = Filter.has_more_likes(None, video)
        self.assertTrue(result)

    def test_min_comments(self):
        video = {'comments_count': 100}
        result = Filter.has_min_comments(50, video)
        self.assertTrue(result)
        result = Filter.has_min_comments(150, video)
        self.assertFalse(result)
        result = Filter.has_min_comments(None, video)
        self.assertTrue(result)

    def test_max_comments(self):
        video = {'comments_count': 100}
        result = Filter.has_under_max_comments(150, video)
        self.assertTrue(result)
        result = Filter.has_under_max_comments(50, video)
        self.assertFalse(result)
        result = Filter.has_under_max_comments(None, video)
        self.assertTrue(result)

    def test_before_date(self):
        video = {'upload_date': '01.02.2000'}
        result = Filter.is_before_date('01.03.2000', video)
        self.assertTrue(result)
        result = Filter.is_before_date('01.01.2000', video)
        self.assertFalse(result)
        result = Filter.is_before_date(None, video)
        self.assertTrue(result)

    def test_after_date(self):
        video = {'upload_date': '01.02.2000'}
        result = Filter.is_after_date('01.01.2000', video)
        self.assertTrue(result)
        result = Filter.is_after_date('01.03.2000', video)
        self.assertFalse(result)
        result = Filter.is_after_date(None, video)
        self.assertTrue(result)

    def test_matching_stream(self):
        video = {'streams': Pafy}
        video['streams'].allstreams = ['normal@200x200', 'audio@128k']

        result = Filter.return_matching_stream('normal@200x200', video)
        self.assertEqual('normal@200x200', result)
        result = Filter.return_matching_stream('normal@1200x1200', video)
        self.assertIsNone(result)

    @patch('filters.Filter.return_matching_stream')
    @patch('pafy.Pafy.getbestaudio')
    @patch('pafy.Pafy.getbest')
    def test_setting_format_and_quality(self, mock_getbest, mock_bestaudio,
                                        mock_match_stream):
        mock_getbest.return_value = 'OK'
        mock_bestaudio.return_value = 'OK'
        mock_match_stream.return_value = 'OK'

        playlists = Filter.set_format_and_quality('normal', None, self.playlists)
        for pl, videos in playlists.items():
            for video in videos:
                self.assertEqual('OK', video['selected_stream'])

    def test_selected_filter(self):
        pass


if __name__ == "__main__":
    unittest.main()
