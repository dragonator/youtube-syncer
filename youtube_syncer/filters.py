class Filter():

    @classmethod
    def filter_all(cls, filters, playlists):
        filtered_playlists = {}

        if filters['selected'] is not None:
            selected_videos = cls.filter_selected(filters['selected'], playlists)
        else:
            selected_videos = playlists

        for playlist, videos in selected_videos.items():
            filtered_playlists[playlist] = []
            for video in videos:
                results = [
                    cls.has_min_likes(filters['min_likes'], video),
                    cls.has_under_max_likes(filters['max_likes'], video),
                    cls.has_min_length(filters['min_length'], video),
                    cls.has_under_max_length(filters['max_length'], video),
                    cls.has_min_views(filters['min_views'], video),
                    cls.has_under_max_views(filters['max_views'], video),
                    cls.has_more_likes(filters['likes_dislikes_difference'], video),
                    cls.has_min_comments(filters['min_comments'], video),
                    cls.has_under_max_comments(filters['max_comments'], video),
                    cls.is_before_date(filters['before_date'], video),
                    cls.is_after_date(filters['after_date'], video)
                ]
                if all(results):
                    filtered_playlists[playlist].append(video)

        if filters['stream_format'] is not None:
            filtered_playlists = \
                cls.set_format_and_quality(filters['stream_format'],
                                           filters['stream_quality'],
                                           filtered_playlists)

        return filtered_playlists

    @classmethod
    def has_min_likes(cls, min_likes, video):
        if min_likes is None:
            return True
        return video["likes"] >= min_likes

    @classmethod
    def has_under_max_likes(cls, max_likes, video):
        if max_likes is None:
            return True
        return video["likes"] <= max_likes

    @classmethod
    def has_min_length(cls, min_length, video):
        if min_length is None:
            return True
        min_length = min_length*60
        return video["length_seconds"] >= min_length

    @classmethod
    def has_under_max_length(cls, max_length, video):
        if max_length is None:
            return True
        max_length = max_length*60
        return video["length_seconds"] <= max_length

    @classmethod
    def has_min_views(cls, min_views, video):
        if min_views is None:
            return True
        return video["views"] >= min_views

    @classmethod
    def has_under_max_views(cls, max_views, video):
        if max_views is None:
            return True
        return video["views"] <= max_views

    @classmethod
    def has_more_likes(cls, difference, video):
        if difference is None:
            return True
        return video["likes"]-video["dislikes"] >= difference

    @classmethod
    def has_min_comments(cls, min_comments_count, video):
        if min_comments_count is None:
            return True
        return video["comments_count"] >= min_comments_count

    @classmethod
    def has_under_max_comments(cls, max_comments_count, video):
        if max_comments_count is None:
            return True
        return video["comments_count"] <= max_comments_count

    @classmethod
    def is_before_date(cls, before_date, video):
        if before_date is None:
            return True
        before_date = before_date.split(".")
        before_date = (int(before_date[2])*10000 +
                       int(before_date[1])*100 +
                       int(before_date[0]))
        video_date = video["upload_date"].split(".")
        video_date = (int(video_date[2])*10000 +
                      int(video_date[1])*100 +
                      int(video_date[0]))

        return video_date < before_date

    @classmethod
    def is_after_date(cls, after_date, video):
        if after_date is None:
            return True
        after_date = after_date.split(".")
        after_date = (int(after_date[2])*10000 +
                      int(after_date[1])*100 +
                      int(after_date[0]))
        video_date = video["upload_date"].split(".")
        video_date = (int(video_date[2])*10000 +
                      int(video_date[1])*100 +
                      int(video_date[0]))

        return video_date > after_date

    @classmethod
    def return_matching_stream(cls, stream_repr, video):
        selected_stream = None
        for stream in video['streams'].allstreams:
            if stream_repr == str(stream):
                selected_stream = stream
                break

        return selected_stream

    @classmethod
    def set_format_and_quality(cls, stream_format, stream_quality, playlists):
        filtered_playlists = {}
        for playlist, videos in playlists.items():
            filtered_playlists[playlist] = []
            for video in videos:
                selected_stream = None
                if stream_quality is None and stream_format == "normal":
                    selected_stream = video['streams'].getbest()
                elif stream_quality is None and stream_format == "audio":
                    selected_stream = video['streams'].getbestaudio()
                else:
                    full_stream_name = stream_format + ':' + stream_quality
                    selected_stream = \
                        cls.return_matching_stream(full_stream_name, video)

                if selected_stream is not None:
                    filtered_video = video
                    filtered_video['selected_stream'] = selected_stream
                    filtered_playlists[playlist].append(filtered_video)

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
