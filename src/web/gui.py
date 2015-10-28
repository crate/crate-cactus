# -*- coding: utf-8; -*-
# vi: set encoding=utf-8

import os
import subprocess
from threading import Thread
try:
    from Tkinter import *
except ImportError:
    # Python 3
    from tkinter import *

class Application(Frame):

    _running = False

    thread_cactus = None
    thread_resize = None
    web_dir = os.path.join(os.getcwd(), 'site')

    def __init__(self, master=None):
        Frame.__init__(self, master=master)
        self.pack()
        self.layout()

    def layout(self):
        self.btn_quit = Button(self)
        self.btn_quit["text"] = "Quit"
        self.btn_quit["command"] =  self.on_close

        self.btn_quit.pack({"side": "left"})

        self.btn_start_stop = Button(self)
        self.btn_start_stop["text"] = "Start"
        self.btn_start_stop["command"] = self.on_start_stop

        self.btn_start_stop.pack({"side": "left"})

    def _set_running(self, running):
        self._running = running
        self.btn_start_stop["text"] = self._running and "Stop" or "Start"

    def _start_cactus(self):
        from cactus.cli import main
        main(['serve',
              '-i',
              '--path', self.web_dir,
              '--config', os.path.join(self.web_dir, 'config.json')])

    def _start_resize(self):
        from web.resize import resize
        resize(['-d', os.path.join(self.web_dir, 'pages')])

    def on_start_stop(self):
        if self._running:
            self.on_stop()
        else:
            self.on_start()

    def on_start(self):
        # start Cactus in new thread
        if not self.thread_cactus:
            print('Starting Cactus server ...')
            self.thread_cactus = Thread(name='Thread-Cactus',
                                        target=self._start_cactus)
            self.thread_cactus.daemon = True
            self.thread_cactus.start()
            #p = subprocess.Popen(args=['open', 'http://localhost:8000'],
            #                     stdout=subprocess.PIPE,
            #                     stderr=subprocess.PIPE)
            #out, err = p.communicate()
        else:
            print('Cactus server already running.')
        # start resize daemon in new thread
        if not self.thread_resize:
            print('Starting resize daemon ...')
            self.thread_resize = Thread(name='Thread-Resize',
                                        target=self._start_resize)
            self.thread_resize.daemon = True
            self.thread_resize.start()
        else:
            print('Resize daemon already running.')
        self._set_running(True)

    def on_stop(self):
        if self.thread_cactus and self.thread_cactus.is_alive():
            print('Stopping Cactus server ...')
            self.thread_cactus.join(timeout=1)
            print('Stopped')
        else:
            print('Cactus server not running.')
        self.thread_cactus = None
        if self.thread_resize and self.thread_resize.is_alive():
            print('Stopping resize daemon ...')
            self.thread_resize.join(timeout=1)
            print('Stopped')
        else:
            print('Resize daemon not running.')
        self.thread_resize = None
        self._set_running(False)

    def on_close(self):
        self.on_stop()
        self.quit()


def main():
    root = Tk()
    app = Application(master=root)
    app.mainloop()
    root.destroy()


if __name__ == '__main__':
    main()

