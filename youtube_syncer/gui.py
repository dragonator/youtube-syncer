import sys
from functools import partial

from PySide import QtGui, QtCore

from youtube_syncer import YTSyncer


class MainWindow(QtGui.QMainWindow):
    """
    Dictionary containing checkbuttons for playlists and videos
    """
    playlists_checkboxes = dict()
    """
    YTSyncer object containing all the information of the videos
    and playlists that is needed
    """
    yt_syncer = None

    def __init__(self):
        self.yt_syncer = YTSyncer()

        super(MainWindow, self).__init__()
        self.setWindowTitle("YouTube Syncer")
        self.setGeometry(350, 350, 500, 500)

        self.master_layout = QtGui.QVBoxLayout()
        self.central_widget = QtGui.QWidget(self)
        self.central_widget.setLayout(self.master_layout)
        self.setCentralWidget(self.central_widget)

        self.master_layout.addLayout(self._panel_url_header())
        self.master_layout.addWidget(self._panel_checkboxes())
        self.master_layout.addLayout(self._panel_buttons_footer())
        self.setLayout(self.master_layout)

    def _panel_url_header(self):
        url_header = QtGui.QHBoxLayout()

        url_label = QtGui.QLabel("URL")
        url_header.addWidget(url_label)

        self.url_text_box = QtGui.QLineEdit()
        url_header.addWidget(self.url_text_box)

        load_videos_btn = QtGui.QPushButton("Load Videos")
        load_videos_btn.clicked.connect(self._load_videos)
        url_header.addWidget(load_videos_btn)

        return url_header

    def _panel_checkboxes(self):
        self.checkboxes_layout = QtGui.QFormLayout()
        checkboxes_container = QtGui.QWidget()
        checkboxes_container.setLayout(self.checkboxes_layout)

        scroll_area = QtGui.QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(checkboxes_container)

        return scroll_area

    def _panel_buttons_footer(self):
        footer = QtGui.QVBoxLayout()

        browse_direcotories_layout = QtGui.QHBoxLayout()
        target_label = QtGui.QLabel("Save to:")
        browse_direcotories_layout.addWidget(target_label)
        self.target_text_box = QtGui.QLineEdit()
        browse_direcotories_layout.addWidget(self.target_text_box)
        browse_button = QtGui.QPushButton("Browse")
        browse_button.clicked.connect(self._pop_up_browser_dialog)
        browse_direcotories_layout.addWidget(browse_button)

        footer.addLayout(browse_direcotories_layout)

        buttons_layout = QtGui.QHBoxLayout()
        buttons_layout.addStretch(1)
        download_button = QtGui.QPushButton("Download")
        download_button.clicked.connect(self.download_selected)
        buttons_layout.addWidget(download_button)

        footer.addLayout(buttons_layout)

        return footer

    def _pop_up_browser_dialog(self):
        directory = \
            QtGui.QFileDialog.getExistingDirectory(self,
                                                   "Save to: "
                                                   "Select Directory")
        self.target_text_box.setText(directory)

    def _load_videos(self):
        url = self.url_text_box.text()
        self.yt_syncer = YTSyncer(url)
        self._add_checkboxes(self.yt_syncer.playlists)

    def download_selected(self):
        self.yt_syncer.download_here = self.target_text_box.text()
        self.yt_syncer.download_videos()

    def _add_checkboxes(self, playlists):
        self.playlists_checkboxes = dict()
        for playlist, videos in playlists.items():
            playlist_info = dict(checkbutton=None, videos=list())

            playlist_info['checkbutton'] = QtGui.QCheckBox(playlist)
            playlist_info['checkbutton'].toggle()
            playlist_info['checkbutton'].stateChanged\
                .connect(partial(self._toggle_playlist_cb, playlist))
            self.checkboxes_layout.addRow(playlist_info['checkbutton'])

            videos_checkboxes_container = QtGui.QVBoxLayout()
            videos_checkboxes_container.setContentsMargins(15, 0, 0, 0)

            for video in videos:
                video_cb = QtGui.QCheckBox(video['title'])
                video_cb.toggle()
                video_cb.stateChanged\
                    .connect(partial(self._toggle_video_cb, video))
                videos_checkboxes_container.addWidget(video_cb)
                playlist_info['videos'].append(video_cb)

            self.checkboxes_layout.addRow(videos_checkboxes_container)
            self.playlists_checkboxes[playlist] = playlist_info

    def _toggle_playlist_cb(self, playlist, state):
        state = self.playlists_checkboxes[playlist]['checkbutton'].checkState()
        videos_checkboxes = self.playlists_checkboxes[playlist]['videos']
        for index, video in enumerate(videos_checkboxes):
            video.setCheckState(state)
            self.yt_syncer.playlists[playlist][index]['is_for_download'] =\
                bool(state)

    def _toggle_video_cb(self, video, state):
        video['is_for_download'] = bool(state)


def main():
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
