# built using vlc example as a starting point
# https://git.videolan.org/?p=vlc/bindings/python.git;a=blob;f=examples/tkvlc.py;h=55314cab09948fc2b7c84f14a76c6d1a7cbba127;hb=HEAD

from time import sleep
import tkinter as tk
import vlc
import sys
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os
import pathlib
from threading import Thread, Event
import time
import platform

# video = VideoPlayer("E:/grontisio/python/vidPlayer/fraktal.mp4")
# video.play()

class ttkTimer(Thread):
    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        self.stopFlag = Event()
        self.tick = tick
        self.iters = 0

    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()

    def stop(self):
        self.stopFlag.set()

    def get(self):
        return self.iters


class VideoPlayer (tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.parent.title("PythonVLCPlayer")

        # Menu Bar
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="Open", underline=0, command=self.OnOpen)
        fileMenu.add_command(label="Exit", underline=1, command=_quit)
        menubar.add_cascade(label="File", menu=fileMenu)

        # Control panels
        self.player = None
        self.videopanel = ttk.Frame(self.parent)
        self.canvas = tk.Canvas(self.videopanel).pack(fill=tk.BOTH, expand=1)
        self.videopanel.pack(fill=tk.BOTH, expand=1)

        ctrlPanel = ttk.Frame(self.parent)
        pause = ttk.Button(ctrlPanel, text="Pause", command=self.OnPause)
        play = ttk.Button(ctrlPanel, text="Play", command=self.OnPlay)
        stop = ttk.Button(ctrlPanel, text="Stop", command=self.OnStop)
        volume = ttk.Button(ctrlPanel, text="Volume", command=self.OnSetVolume)
        pause.pack(side=tk.LEFT)
        play.pack(side=tk.LEFT)
        stop.pack(side=tk.LEFT)
        volume.pack(side=tk.LEFT)
        self.volume_var = tk.IntVar()
        self.volslider = tk.Scale(
            ctrlPanel, variable=self.volume_var, command=self.volume_sel,
            from_=0, to=100, orient=tk.HORIZONTAL, length=100
        )
        self.volslider.pack(side=tk.LEFT)
        ctrlPanel.pack(side=tk.BOTTOM)

        ctrlPanel2 = ttk.Frame(self.parent)
        self.scale_var = tk.DoubleVar()
        self.timeslider_last_val = ""
        self.timeslider = tk.Scale(
            ctrlPanel2, variable=self.scale_var, command=self.scale_sel,
            from_=0, to=1000, orient=tk.HORIZONTAL, length=500
        )
        self.timeslider.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
        self.timeslider_last_update = time.time()
        ctrlPanel2.pack(side=tk.BOTTOM, fill=tk.X)

        # VLC controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        self.timer = ttkTimer(self.OnTimer, 1.0)
        self.timer.start()
        self.parent.update()

    # TODO: (bugfix) if a loaded video file is being played (or even paused after being played),
    #       and the user tries to open another video file, the program will hang upon clicking
    #       open in the menu.
    #       This error does not occur when the user clicks Stop before trying to open a file.
    def OnOpen(self):
        self.OnStop()

        p = pathlib.Path(os.path.expanduser("~"))
        fullname = askopenfilename(initialdir = p, title = "choose your file", filetypes = (("all files", "*.*"), ("mp4 files","*.mp4")))
        if os.path.isfile(fullname):
            dirname = os.path.dirname(fullname)
            filename = os.path.basename(fullname)

            self.media = self.Instance.media_new(str(os.path.join(dirname, filename)))
            self.player.set_media(self.media)

            if platform.system() == 'Windows':
                self.player.set_hwnd(self.GetHandle())
            else:
                self.player.set_xwindow(self.GetHandle())
            self.OnPlay()

            self.volslider.set(self.player.audio_get_volume())

    def OnExit(self, evt):
        self.Close()

    def OnPlay(self):
        if not self.player.get_media():
            self.OnOpen()
        else:
            if self.player.play() == -1:
                self.errorDialog("Unable to play.")

    def GetHandle(self):
        return self.videopanel.winfo_id()

    def OnPause(self):
        self.player.pause()

    def OnStop(self):
        self.player.stop()
        self.timeslider.set(0)

    def OnTimer(self):
        if self.player == None:
            return

        length = self.player.get_length()
        dbl = length * 0.001
        self.timeslider.config(to=dbl)

        tyme = self.player.get_time()
        if tyme == -1:
            tyme = 0
        dbl = tyme * 0.001
        self.timeslider_last_val = ("%.0f" % dbl) + ".0"
        if time.time() > (self.timeslider_last_update + 2.0):
            self.timeslider.set(dbl)

    def scale_sel(self, evt):
        if self.player == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            self.player.set_time(int(mval))

    def volume_sel(self, evt):
        if self.player == None:
            return
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def OnToggleVolume(self, evt):
        is_mute = self.player.audio_get_mute()

        self.player.audio_set_mute(not is_mute)
        self.volume_var.set(self.player.audio_get_volume())

    def OnSetVolume(self):
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def errorDialog(self, errorMessage):
        tk.tkMessageBox.showerror(self, 'Error', errorMessage)

def tkGetRoot():
    if not hasattr(tkGetRoot, "root"):
        tkGetRoot.root = tk.Tk()
    return tkGetRoot.root

def _quit():
    print("quitting:bye")
    root = tkGetRoot()
    root.quit()
    root.destroy()
    os._exit(1)


if __name__ == "__main__":
    root = tkGetRoot()

    # root.attributes("-fullscreen", True) # set GUI to fullscreen

    root.protocol("WM_DELETE_WINDOW", _quit)

    player = VideoPlayer(root)

    root.mainloop()