import sys

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

    def _load_videos(self):
        url = self.url_text_box.text()
        self.yt_syncer = YTSyncer(url)
        self._add_checkboxes(self.yt_syncer.playlists)

    def _add_checkboxes(self, playlists):
        self.playlists_checkboxes = dict()
        for playlist, videos in playlists.items():
            playlist_info = dict(checkbutton=None, videos=list())

            playlist_info['checkbutton'] = QtGui.QCheckBox(playlist)
            self.checkboxes_layout.addRow(playlist_info['checkbutton'])
            videos_checkboxes_container = QtGui.QVBoxLayout()
            videos_checkboxes_container.setContentsMargins(15, 0, 0, 0)
            for video in videos:
                video_cb = QtGui.QCheckBox(video['title'])
                # self.checkboxes_layout.addRow(video_cb)
                videos_checkboxes_container.addWidget(video_cb)
                playlist_info['videos'].append(video_cb)

            self.checkboxes_layout.addRow(videos_checkboxes_container)
            self.playlists_checkboxes[playlist] = playlist_info


def main():
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
