# videoPlayer
video player app using python &amp; python-vlc module

I have a lot of movies and TV shows downloaded onto a PC, and thought that it would be nice to have a user friendly way to select, play, and keep track of what has been watched (something that I felt I did not currently have while using VLC to play my videos). 

I discovered the python-vlc module which provides VLC bindings for python, and also discovered a useful example using tkinter for GUI upon which I spent time studying and replicating. The example provides a basic GUI that allows for opening a media file, and then instantiates a VLC player within the tkinter GUI frame.

Features I would like to add:
* GUI display of all media files and directories within a specified media folder
* Application state - keep track of what has been watched (for example, if watching a TV series, keep track of most recent episode watched, and how much has been watched of an episode/film)
* If watching a series: GUI options to view all episodes, next/prev button
