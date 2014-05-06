try:
    import tkinter as tk
except:
    import Tkinter as tk
import pafy
import re


class AutoScrollbar(tk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")


class ScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, kwargs)

        # Vertical scroll
        vscrollbar = tk.Scrollbar(self,
                                  bg='grey', bd=0,
                                  activebackground='#A3A3A3',
                                  troughcolor='#444444',
                                  width=16, orient=tk.VERTICAL)
        vscrollbar.pack(side='right', fill="y",  expand="false")
        # Canvas to hold the 'scrollable' frame
        self.canvas = tk.Canvas(self,
                                bg='#444444', bd=0,
                                height=350,
                                highlightthickness=0,
                                yscrollcommand=vscrollbar.set)
        self.canvas.pack(side="left", fill="both", expand="true")

        vscrollbar.config(command=self.canvas.yview)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # The frame inside the canvas (the container)
        self.interior = tk.Frame(self.canvas, kwargs)
        self.canvas.create_window(0, 0, window=self.interior, anchor="nw")

        self.bind('<Configure>', self.set_scrollregion)

    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.config(scrollregion=self.canvas.bbox('all'))


class Application(tk.Frame):

    playlists = dict()

    def __init__(self, root):
        tk.Frame.__init__(self, root, bg='grey')
        self.url_input = tk.StringVar()
        self.root = root
        self.initUI()

    def initUI(self):
        # Basic window
        self.root.title('YouTube Syncer')
        self.root.configure(bg="grey")
        self.root.geometry('600x500+300+300')
        self.root.resizable(tk.FALSE, tk.FALSE)
        self.grid(sticky=tk.W+tk.E+tk.N+tk.S)

        self.url_header()
        self.checkboxes_container()

    def url_header(self):
        # Header container
        self.url_header = \
            tk.Frame(self,
                     bg='grey',
                     bd=0,
                     highlightthickness=0)
        # URL Label
        self.url_label = \
            tk.Label(self.url_header,
                     text='URL :',
                     bg='grey')
        # URL Entry
        self.url_entry = \
            tk.Entry(self.url_header,
                     textvariable=self.url_input,
                     width=50)
        # Load Videos Button
        self.load_videos_button = \
            tk.Button(self.url_header,
                      text='Load Videos',
                      command=self.load_button_command)
        # Grid widgets
        self.url_header.grid(row=0, column=0,
                             pady=8, padx=15,
                             sticky=tk.E+tk.W)
        self.url_label.grid(row=0, column=0)
        self.url_entry.grid(row=0, column=1, padx=10, sticky=tk.E+tk.W)
        self.load_videos_button.grid(row=0, column=2)

    def checkboxes_container(self):
        self.checkbox_pane = ScrollableFrame(self,
                                             bg='#444444')
        self.checkbox_pane.grid(row=1, column=0,
                                columnspan=3,
                                sticky='nwes')

    def get_filtered_video_info(self, pafy_playlist_item):
        meta_info = pafy_playlist_item['playlist_meta']
        info =\
            dict(title=meta_info['title'],
                 likes=meta_info['likes'],
                 dislikes=meta_info['dislikes'],
                 views=self._to_int(meta_info['views']),
                 upload_time=meta_info['added'],
                 comments_count=self._to_int(meta_info['comments']),
                 length_seconds=meta_info['length_seconds'],
                 rating=meta_info['rating'])
        try:
            info['streams'] = pafy_playlist_item['pafy'].allstreams
            info['for_download'] = pafy_playlist_item['pafy'].getbest()
        except IOError as message:
            message = re.sub(r'\[.+\]', '[ '+info['title']+' ]', str(message))
            print(message)

        return info

    def _to_int(self, string):
        return int(re.sub(r'[^0-9]', '', string))

    def toggle_videos_checkbuttons(self, playlist_title):
        for video in self.playlists[playlist_title]['videos']:
            state = self.playlists[playlist_title]['state'].get()
            if state:
                video['checkbutton'].select()
            else:
                video['checkbutton'].deselect()

    def load_button_command(self):
        frame_to_remove = self.checkbox_pane
        self.checkbox_pane = ScrollableFrame(self,
                                             bg='#444444')
        # Add top padding to the checkbox pane
        padding_up = tk.Frame(self.checkbox_pane.interior,
                              bg='#444444',
                              height=5)
        padding_up.grid()
        # Get playlist information using pafy module
        pafy_playlist_info = pafy.get_playlist(self.url_input.get())
        # Get playlist title
        playlist_title = pafy_playlist_info['title']
        self.playlists[playlist_title] = dict(state=tk.IntVar())
        # Create checkbox for playlist and place it
        self.playlists[playlist_title]['checkbutton'] = \
            tk.Checkbutton(self.checkbox_pane.interior,
                           bg='#444444',
                           fg='#ffffff',
                           bd=0,
                           activebackground='#444444',
                           activeforeground='#ffffff',
                           selectcolor='#777777',
                           highlightthickness=0,
                           highlightbackground='red',
                           text=playlist_title,
                           variable=self.playlists[playlist_title]['state'],
                           command=lambda:
                               self.toggle_videos_checkbuttons(playlist_title)
                           )
        self.playlists[playlist_title]['checkbutton'].grid(sticky=tk.W+tk.N)
        # Create list for videos
        self.playlists[playlist_title]['videos'] = list()
        for video in pafy_playlist_info['items']:
            video_info = self.get_filtered_video_info(video)
            # Create checkbox for a single video and place it
            video_cb = tk.Checkbutton(self.checkbox_pane.interior,
                                      bg='#444444',
                                      fg='#ffffff',
                                      bd=0,
                                      activebackground='#444444',
                                      activeforeground='#ffffff',
                                      selectcolor='#777777',
                                      highlightthickness=0,
                                      highlightbackground='red',
                                      text=video_info['title'],
                                      padx=15)
            video_cb.grid(sticky=tk.W+tk.N)
            # Create video dictionary
            video_dict = dict(checkbutton=video_cb, info=video_info)
            # Add the video dictionary to the playlists videos list
            self.playlists[playlist_title]['videos'].append(video_dict)

        # Add bottom padding to the checkbox pane
        padding_down = tk.Frame(self.checkbox_pane.interior,
                                bg='#444444',
                                height=5)
        padding_down.grid()
        frame_to_remove.grid_remove()
        self.checkbox_pane.grid(row=1, column=0,
                                columnspan=3,
                                sticky='nwes')
