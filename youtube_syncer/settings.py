import os
import json


class Settings():
    _default_settings = {
        "filters": {
            "selected": None,
            "min_likes": None,
            "max_likes": None,
            "min_length": None,
            "max_length": None,
            "min_views": None,
            "max_views": None,
            "likes_dislikes_difference": None,
            "min_comments": None,
            "max_comments": None,
            "before_date": None,
            "after_date": None,
            "stream_format": "normal",
            "stream_quality": None
        },
        "target_directory": os.getcwd()
    }

    def __init__(self):
        try:
            input_settings = open("preferred_settings.json", "r")
            self._default_settings = json.loads(input_settings.read())
            input_settings.close()
        except:
            pass

    def save_settings(self):
        with open("preferred_settings.json", "w") as output_settings:
            json.dump(self.default_settings, output_settings,
                      sort_keys=True, indent=4)

    @property
    def default_settings(self):
        return self._default_settings

    @property
    def default_filters(self):
        return self._default_settings['filters']

    @property
    def default_target_directory(self):
        return self._default_settings['target_directory']

    def set_filters(self, filters):
        self._default_settings['filters'] = filters

    def set_target_directory(self, target_directory):
        self._default_settings['target_directory'] = target_directory
