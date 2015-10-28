# -*- coding: utf-8; -*-
# vi: set encoding=utf-8
#
# Licensed to Crate (https://crate.io) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  Crate licenses
# this file to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
# However, if you have executed another commercial license agreement
# with Crate these terms will supersede the license and you may use the
# software solely pursuant to the terms of the relevant commercial agreement.

import os
from threading import Thread

try:
    # MacPorts Tk problem?
    import tkFileDialog
except ImportError:
    pass

try:
    # Python 2
    from Tkinter import *
except ImportError:
    # Python 3
    from tkinter import *


class Application(Frame):

    thread_cactus = None
    thread_resize = None
    web_dir = os.path.join(os.getcwd(), 'site')

    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.parent.title(kwargs.pop('title'))
        Frame.__init__(self, parent, **kwargs)
        self.layout()
        self._running = False

    def layout(self):

        self.btn_open = Button(self,
                               text='Path to Cactus site',
                               command=self.on_select_path,
                               width=30)
        self.btn_open.grid(padx=5, row=0, column=0)

        self.selected_path = StringVar()
        self.selected_path.set(self.web_dir)

        self.entry_path = Entry(self,
                                textvariable=self.selected_path,
                                fg='black',
                                width=40)
        self.entry_path.grid(padx=5, row=0, column=1)

        self.btn_start_stop = Button(self,
                                     text='Start',
                                     command=self.on_start_stop,
                                     width=30)
        self.btn_start_stop.grid(padx=5, row=1, column=0)

        self.btn_quit = Button(self,
                               text='Quit',
                               command=self.on_close,
                               width=30)
        self.btn_quit.grid(padx=5, row=2, column=0)

        self.dir_opt = {
            'initialdir': '.',
            'mustexist': True,
            'parent': self.parent,
        }

        self.status = StringVar()
        self.status.set('Stopped')

        self.status_lable = Label(self, textvariable=self.status, fg='grey')
        self.status_lable.grid(row=1, column=1, rowspan=1)

    def _set_running(self, running):
        self._running = running
        self.btn_start_stop["text"] = self._running and "Stop" or "Start"
        self.status.set(self._running and 'Running ...' or 'Stopped')

    def _start_cactus(self):
        from cactus.cli import main
        main(['serve',
              '-i',
              '--path', self.selected_path.get(),
              '--config', os.path.join(self.web_dir, 'config.json')])

    def _start_resize(self):
        from web.resize import resize
        resize(['-d', os.path.join(self.selected_path.get(), 'pages')])

    def on_start_stop(self):
        if self._running:
            self.status.set('Stopping ...')
            self.on_stop()
        else:
            self.status.set('Starting ...')
            self.on_start()

    def on_start(self):
        # start Cactus in new thread
        if not self.thread_cactus:
            print('Starting Cactus server ...')
            self.thread_cactus = Thread(name='Thread-Cactus',
                                        target=self._start_cactus)
            self.thread_cactus.daemon = True
            self.thread_cactus.start()
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

    def on_select_path(self):
        self.web_dir = tkFileDialog.askdirectory(**self.dir_opt)
        self.selected_path.set(self.web_dir)

def main():
    root = Tk()
    app = Application(root, title='Crate Cactus')
    app.pack(side='top', fill='both', expand=True)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()
        root.destroy()
        sys.exit(0)

if __name__ == '__main__':
    main()
