class Filter():

    @classmethod
    def by_min_likes(cls, min_likes, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["likes"] >= min_likes:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_max_likes(cls, max_likes, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["likes"] <= max_likes:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_min_length_in_minutes(cls, min_length, playlists):
        min_length = min_length*60
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["length_seconds"] >= min_length:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_max_langth_in_minutes(cls, max_length, playlists):
        max_length = max_length*60
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["length_seconds"] <= max_length:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_min_views(cls, min_views, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["views"] >= min_views:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_max_views(cls, max_views, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["views"] <= max_views:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_more_likes_than_dislikes(cls, difference, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["likes"]-video["dislikes"] >= difference:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_min_comments(cls, min_comments_count, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["comments_count"] >= min_comments_count:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_max_comments(cls, max_comments_count, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                if video["comments_count"] <= max_comments_count:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def filter_selected(cls, selected_videos, playlists):
        filtered_playlists = {}
        for playlist_index, playlist in enumerate(playlists.keys()):
            if playlist_index in selected_videos.keys():
                filtered_playlists[playlist] = []
                for video_index, video in enumerate(playlists[playlist]):
                    if video_index in selected_videos[playlist_index]:
                        filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_before_date(cls, before_date, playlists):
        filtered_playlists = {}
        before_date = before_date.split(".")
        before_date = (int(before_date[2])*10000 +
                       int(before_date[1])*100 +
                       int(before_date[0]))
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                video_date = video["upload_date"].split(".")
                video_date = (int(video_date[2])*10000 +
                              int(video_date[1])*100 +
                              int(video_date[0]))
                if video_date < before_date:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_after_date(cls, after_date, playlists):
        filtered_playlists = {}
        after_date = after_date.split(".")
        after_date = (int(after_date[2])*10000 +
                      int(after_date[1])*100 +
                      int(after_date[0]))
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                video_date = video["upload_date"].split(".")
                video_date = (int(video_date[2])*10000 +
                              int(video_date[1])*100 +
                              int(video_date[0]))
                if video_date < after_date:
                    filtered_playlists[playlist].append(video)

        return filtered_playlists

    @classmethod
    def by_format_and_quality(cls, stream_format, stream_quality, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                selected_stream = None
                if stream_quality is None:
                    if stream_format == "normal":
                        selected_stream = video['pafy'].getbest()
                    elif stream_format == "audio":
                        selected_stream = video['pafy'].getbestaudio()
                else:
                    full_stream_name = '{}{}{}'.format(stream_format, ':',
                                                       stream_quality)
                    for stream in video['streams'].allstreams:
                        if full_stream_name == str(stream):
                            selected_stream = stream
                            break

                if selected_stream is not None:
                    filtered_video = video
                    filtered_video['selected_stream'] = selected_stream
                    filtered_playlists[playlist].append(filtered_video)

        return filtered_playlists
