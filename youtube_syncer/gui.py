#!/usr/bin/env python

import sys
from functools import partial
import threading
import time

from PyQt4 import QtGui, QtCore

from youtube_syncer import YTSyncer


class MainWindow(QtGui.QMainWindow):
    """
    Dictionary containing checkbuttons for playlists and videos
    """
    playlists_checkboxes = {}
    """
    YTSyncer object containing all the information of the videos
    and playlists that is needed
    """
    yt_syncer = None
    MIN_BUTTON_WIDTH = 100
    MIN_BUTTON_HEIGHT = 30
    MIN_LINEEDIT_HEIGHT = 30

    statusChanged = QtCore.pyqtSignal()

    def __init__(self):
        self.yt_syncer = YTSyncer()
        self.initGui()
        self._tray_icon_and_menu()
        status_handler = threading.Thread(target=self.check_for_status_updates)
        status_handler.daemon = True
        status_handler.start()

    def initGui(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("YouTube Syncer")
        self.setGeometry(350, 350, 850, 600)

        self.left_layout = QtGui.QVBoxLayout()
        self.left_layout.addLayout(self._panel_url_header)
        self.left_layout.addWidget(self._panel_checkboxes)
        self.left_layout.addLayout(self._panel_buttons_footer)

        self.right_layout = QtGui.QVBoxLayout()
        self.right_layout.addWidget(self._right_panel)

        self.status_bar = QtGui.QStatusBar()
        self.statusChanged.connect(self.update_status)

        self.master_layout = QtGui.QGridLayout()
        self.master_layout.addLayout(self.left_layout, 0, 0)
        self.master_layout.addLayout(self.right_layout, 0, 1)
        self.master_layout.addWidget(self.status_bar, 1, 0, 1, 2)

        self.central_widget = QtGui.QWidget(self)
        self.central_widget.setLayout(self.master_layout)
        self.setCentralWidget(self.central_widget)
        # self.setLayout(self.master_layout)

    @property
    def _file_formats_groupbox(self):
        file_format_layout = QtGui.QGridLayout()

        file_format_groupbox = QtGui.QGroupBox("File format and quality")
        file_format_groupbox.setMaximumWidth(400)
        file_format_groupbox.setLayout(file_format_layout)

        self.radio_buttons = {}
        self.radio_buttons['normal'] = QtGui.QRadioButton("Video")
        self.radio_buttons['normal'].setMinimumWidth(80)
        self.radio_buttons['normal'].clicked.connect(self.update_streams_list)
        # self.radio_video = QtGui.QRadioButton("Video only")
        # self.radio_video.clicked.connect(self.update_streams_list)
        self.radio_buttons['audio'] = QtGui.QRadioButton("Audio")
        self.radio_buttons['audio'].setMinimumWidth(80)
        self.radio_buttons['audio'].clicked.connect(self.update_streams_list)

        radio_buttons_group = QtGui.QButtonGroup()
        radio_buttons_group.addButton(self.radio_buttons['normal'])
        # radio_buttons_group.addButton(self.radio_video)
        radio_buttons_group.addButton(self.radio_buttons['audio'])

        select_best = QtGui.QCheckBox("Auto select best available stream")
        select_best.stateChanged.connect(self.auto_select_best_stream)

        self.streams_list = QtGui.QListWidget()
        self.streams_list.setMinimumHeight(150)
        self.streams_list.setEnabled(False)
        self.streams_list.itemClicked.connect(self.set_stream_quality)

        file_format_layout.addWidget(self.radio_buttons['normal'], 0, 0)
        # file_format_layout.addWidget(self.radio_video)
        file_format_layout.addWidget(self.radio_buttons['audio'], 1, 0)
        file_format_layout.addWidget(select_best, 3, 1, 1, 2)
        file_format_layout.addWidget(self.streams_list, 0, 1, 3, 1)

        self.radio_buttons[self.yt_syncer.filters['stream_format']].click()
        select_best.click()

        return file_format_groupbox

    @property
    def _filters_groupbox(self):
        filters_layout = QtGui.QVBoxLayout()
        self.filters_groupbox = QtGui.QGroupBox("Enable filters")
        self.filters_groupbox.setCheckable(True)
        self.filters_groupbox.setChecked(False)
        self.filters_groupbox.clicked.connect(self.filters_checkbox_clicked)
        self.filters_groupbox.setMaximumWidth(400)
        self.filters_groupbox.setLayout(filters_layout)

        filters_strings = [
            ("Minimum likes :", "min_likes"),
            ("Maximum likes :", "max_likes"),
            ("Minimum length (minutes) :", "min_length"),
            ("Maximum length (minutes) :", "max_length"),
            ("Minimum views :", "min_views"),
            ("Maximum views :", "max_views"),
            ("More likes than dislikes (difference) :",
             "likes_dislikes_difference"),
            ("Minimum comments :", "min_comments"),
            ("Maximum comments :", "max_comments")
        ]

        for string_tuple in filters_strings:
            current_line = QtGui.QHBoxLayout()
            filter_title = string_tuple[0]
            filter_key = string_tuple[1]

            le = QtGui.QLineEdit()
            le.setMinimumHeight(self.MIN_LINEEDIT_HEIGHT)
            le.setEnabled(False)
            le.setFixedWidth(100)
            le.textChanged.connect(partial(self.set_filter_value,
                                           le, filter_key))

            cb = QtGui.QCheckBox(filter_title)
            cb.stateChanged.connect(partial(self.disable_filter,
                                    le, filter_key))

            current_line.addWidget(cb)
            current_line.addStretch(1)
            current_line.addWidget(le)
            filters_layout.addLayout(current_line)

        filters_strings = [
            ("Before given date :", "before_date"),
            ("After given date :", "after_date")
        ]
        for string_tuple in filters_strings:
            filter_title = string_tuple[0]
            filter_key = string_tuple[1]

            calendar = QtGui.QCalendarWidget()
            calendar.setEnabled(False)
            calendar.setMinimumHeight(200)
            calendar.clicked.connect(partial(self.set_filter_value,
                                             calendar, filter_key))

            cb = QtGui.QCheckBox(filter_title)
            cb.stateChanged.connect(partial(self.disable_filter,
                                            calendar, filter_key))

            filters_layout.addWidget(cb)
            filters_layout.addWidget(calendar)

        return self.filters_groupbox

    @property
    def _panel_url_header(self):
        url_header = QtGui.QHBoxLayout()

        self.url_text_box = QtGui.QLineEdit()
        self.url_text_box.setMinimumHeight(self.MIN_LINEEDIT_HEIGHT)

        load_videos_button = QtGui.QPushButton("Load Videos")
        load_videos_button.setMinimumWidth(self.MIN_BUTTON_WIDTH)
        load_videos_button.setMinimumHeight(self.MIN_BUTTON_HEIGHT)
        load_videos_button.clicked.connect(self.load_videos)

        url_header.addWidget(QtGui.QLabel("URL"))
        url_header.addWidget(self.url_text_box)
        url_header.addWidget(load_videos_button)

        return url_header

    @property
    def _panel_checkboxes(self):
        self.checkboxes_layout = QtGui.QFormLayout()
        checkboxes_container = QtGui.QWidget()
        checkboxes_container.setLayout(self.checkboxes_layout)

        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(checkboxes_container)
        scroll_area.setFocusPolicy(QtCore.Qt.NoFocus)

        return scroll_area

    @property
    def _panel_buttons_footer(self):
        footer = QtGui.QVBoxLayout()
        browse_direcotories_layout = QtGui.QHBoxLayout()

        target_label = QtGui.QLabel("Save to:")
        self.target_text_box = QtGui.QLineEdit()
        self.target_text_box.setMinimumHeight(self.MIN_LINEEDIT_HEIGHT)

        browse_button = QtGui.QPushButton("Browse")
        browse_button.setMinimumWidth(self.MIN_BUTTON_WIDTH)
        browse_button.setMinimumHeight(self.MIN_BUTTON_HEIGHT)
        browse_button.clicked.connect(self._show_get_dir_dialog)

        browse_direcotories_layout.addWidget(target_label)
        browse_direcotories_layout.addWidget(self.target_text_box)
        browse_direcotories_layout.addWidget(browse_button)

        buttons_layout = QtGui.QHBoxLayout()
        download_button = QtGui.QPushButton("Download")
        download_button.setMinimumWidth(self.MIN_BUTTON_WIDTH)
        download_button.setMinimumHeight(self.MIN_BUTTON_HEIGHT)
        download_button.clicked.connect(self.download)

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(download_button)

        footer.addLayout(browse_direcotories_layout)
        footer.addLayout(buttons_layout)

        return footer

    @property
    def _right_panel(self):
        master_layout = QtGui.QVBoxLayout()
        master_layout.addWidget(self._file_formats_groupbox)
        master_layout.addWidget(self._filters_groupbox)

        master = QtGui.QWidget()
        master.setLayout(master_layout)

        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(404)
        scroll_area.setWidget(master)
        scroll_area.setFocusPolicy(QtCore.Qt.NoFocus)

        return scroll_area

    def _show_get_dir_dialog(self):
        title = "Save to: Select Directory"
        directory = QtGui.QFileDialog.getExistingDirectory(self, title)
        self.target_text_box.setText(directory)

    def _tray_icon_and_menu(self):
        self.icon = QtGui.QSystemTrayIcon(QtGui.QIcon('img/icon.jpg'))
        self.icon.show()
        self.icon.activated.connect(self.showNormal)

        tray_menu = QtGui.QMenu()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(sys.exit)

        self.icon.setContextMenu(tray_menu)

    def add_checkboxes(self, playlists):
        self.clear_layout(self.checkboxes_layout)
        self.playlists_checkboxes = {}

        for playlist, videos in playlists.items():
            playlist_info = {"checkbutton": None, "videos": []}

            playlist_info['checkbutton'] = QtGui.QCheckBox(playlist)
            playlist_info['checkbutton'].toggle()
            playlist_info['checkbutton'].stateChanged\
                .connect(partial(self.toggle_playlist_cb, playlist))

            videos_checkboxes_container = QtGui.QVBoxLayout()
            videos_checkboxes_container.setContentsMargins(15, 0, 0, 0)

            for video in videos:
                video_cb = QtGui.QCheckBox(video['title'])
                video_cb.toggle()
                # video_cb.stateChanged\
                #    .connect(partial(self._toggle_video_cb, video))
                videos_checkboxes_container.addWidget(video_cb)
                playlist_info['videos'].append(video_cb)

            self.checkboxes_layout.addRow(playlist_info['checkbutton'])
            self.checkboxes_layout.addRow(videos_checkboxes_container)
            self.playlists_checkboxes[playlist] = playlist_info

    def auto_select_best_stream(self, state):
        state = bool(state)
        self.streams_list.setEnabled(not state)
        if state:
            self.set_stream_quality(None)
        else:
            self.set_stream_quality(self.streams_list.currentItem())

    def changeEvent(self, e):
        if(type(e) == QtCore.QEvent.WindowStateChange and self.isMinimized()):
            self.hide()
            e.accept()
        else:
            QtGui.QMainWindow.changeEvent(self, e)

    def check_for_status_updates(self):
        while True:
            try:
                if self.yt_syncer.status != self.status_bar.currentMessage():
                    self.statusChanged.emit()
                time.sleep(1)
            except RuntimeError:
                break

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())

    def disable_filter(self, value_widget, filter_key, state):
        value = None
        if state:
            try:
                value = int(value_widget.text())
            except AttributeError:
                value = value_widget.selectedDate().toString("d.MM.yy")
            except ValueError:
                value = None

        value_widget.setEnabled(bool(state))
        self.yt_syncer.filters[filter_key] = value

    def download(self):
        self.yt_syncer.filters["selected"] = self.get_selected_videos()

        self.yt_syncer.filter_videos(self.yt_syncer.filters)
        self.yt_syncer.target_directory = self.target_text_box.text()
        self.yt_syncer.download_videos()
        """
        for key, value in self.yt_syncer.filters.items():
            print(key, value)
        """
        """
        for fformat, quality in self.yt_syncer.format_and_quality.items():
            print(fformat)
            for qu in quality:
                print("     ", qu)
        """

    def filters_checkbox_clicked(self):
        if self.filters_groupbox.isChecked():
            self.filters_groupbox.setTitle("Disable filters")
        else:
            self.filters_groupbox.setTitle("Enable filters")

    def get_selected_videos(self):
        return {
            pl_index: [vd_id
                       for vd_id, video
                       in enumerate(self.playlists_checkboxes[pl]["videos"])
                       if video.isChecked()]
            for pl_index, pl in enumerate(self.playlists_checkboxes)
            if self.playlists_checkboxes[pl]["checkbutton"].isChecked()
        }

    def load_videos(self):
        url = self.url_text_box.text()
        load = threading.Thread(target=self.yt_syncer.load_playlists,
                                args=(url,))
        load.daemon = True
        load.start()
        while load.isAlive():
            self.update_status()

        self.update_status("Creating checkboxes for videos...")
        self.add_checkboxes(self.yt_syncer.playlists)
        self.filters_groupbox.setEnabled(True)

        self.update_status("Updating streams list...")
        self.update_streams_list()

        self.update_status("Idle")

    def set_filter_value(self, value_widget, filter_key, value):
        if isinstance(value_widget, QtGui.QCalendarWidget):
            value = value.toString("d.MM.yy")
        else:
            if value.isnumeric():
                value = int(value)
            else:
                if len(value) != 0:
                    value_widget.setText("")
                    print("Wrong input")
                value = None

        self.yt_syncer.filters[filter_key] = value

    def set_stream_quality(self, item):
        if item is not None:
            self.yt_syncer.filters['stream_quality'] = item.text()
        else:
            self.yt_syncer.filters['stream_quality'] = None

    def toggle_playlist_cb(self, playlist, state):
        state = self.playlists_checkboxes[playlist]['checkbutton'].checkState()
        videos_checkboxes = self.playlists_checkboxes[playlist]['videos']
        for video in videos_checkboxes:
            video.setCheckState(state)

    def update_status(self, message=None):
        if message is not None:
            self.yt_syncer.set_status(message)
        self.status_bar.showMessage(self.yt_syncer.status)

    def update_streams_list(self):
        for radio_key, radio_btn in self.radio_buttons.items():
            if radio_btn.isChecked():
                key = radio_key
                break
        self.yt_syncer.filters['stream_format'] = key
        self.set_stream_quality(None)
        self.streams_list.clear()
        for stream in self.yt_syncer.format_and_quality[key]:
            lw = QtGui.QListWidgetItem(stream)
            self.streams_list.addItem(lw)


def main():
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
