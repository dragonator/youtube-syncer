youtube-syncer
==============

A program to sync all/some of your youtube videos(or just audio)

Basic functionality
-------------------
youtube-syncer will help you easily download your favourite youtube videos (or even whole playlists) in different file formats.All you need is an URL address to the video or to the playlist page.The program will give you the opportunity to set up synchronization and it will sync your new-liked videos in the chosen file format, quality, directory to be saved and etc. That's an easy way to keep your likes videos up to date and ready to be uploaded on any mobile device you want.

Features
--------
+ GUI version - for easy use by everyone

+ CLI verion - for not so easy use, but for nerds

+ Separate folder arrangement - by downloading a whole playlist youtube-syncer will create folder named by the corresponding playlist in the giver directory and it'll download the files in there

+ Filters - you can filter loaded videos to meet some criteria of your choice
  + by quality
  + by length
  + by comments count
  + by views count
  + by likes/dislikes count
  + by rating
  + by date

+ Synchronization - you'll be able to set up youtube-syncer to check some URL and download new-liked videos

Used modules
------------
+ Pafy - getting information about videos from YouTube ( https://github.com/np1/pafy )
+ PySide - used for GUI version ( http://qt-project.org/wiki/pyside )

Milestone 2
-----------
Untill milestone 2 it will be ready the basic functionality - you will be able to download videos/playlists in given directory and to choose for single video whether to be downloaded or not ( using checkboxes ).
