# -*- coding: utf-8; -*-
# vi: set encoding=utf-8

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

from multiprocessing import set_start_method

import tkinter as tk
from tkinter import filedialog, messagebox

from web.common import Application


class GuiApplication(Application, tk.Frame):

    web_dir = os.path.join(os.path.expanduser('~'), 'crate-web')

    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.parent.title(kwargs.pop('title'))
        tk.Frame.__init__(self, parent, **kwargs)
        self.layout()
        self._running = False

    def layout(self):
        self.btn_open = tk.Button(self,
                                  text='Path to Cactus site',
                                  command=self.on_select_path,
                                  width=30)
        self.btn_open.grid(padx=5, row=0, column=0)

        self.selected_path = tk.StringVar()
        self.selected_path.set(self.web_dir)

        self.entry_path = tk.Entry(self,
                                   textvariable=self.selected_path,
                                   fg='black',
                                   width=40)
        self.entry_path.grid(padx=5, row=0, column=1)

        self.btn_start_stop = tk.Button(self,
                                        text='Start',
                                        command=self.on_start_stop,
                                        width=30)
        self.btn_start_stop.grid(padx=5, row=1, column=0)

        self.btn_quit = tk.Button(self,
                                  text='Quit',
                                  command=self.on_close,
                                  width=30)
        self.btn_quit.grid(padx=5, row=2, column=0)

        self.dir_opt = {
            'initialdir': self.web_dir,
            'mustexist': True,
        }

        self.status = tk.StringVar()
        self.status.set('Stopped')

        self.status_lable = tk.Label(self, textvariable=self.status, fg='grey')
        self.status_lable.grid(row=1, column=1, rowspan=1)

    def _set_running(self, running):
        super(GuiApplication, self)._set_running(running)
        self.btn_start_stop["text"] = self._running and "Stop" or "Start"
        self.status.set(self._running and 'Running ...' or 'Stopped')

    def on_start_stop(self):
        if self._running:
            self.status.set('Stopping ...')
            self.on_stop()
        elif self._check_cactus_dir(self.web_dir):
            self.status.set('Starting ...')
            self.on_start()
        else:
            self._alert('{0} is not a valid Cactus site'.format(self.web_dir))

    def wait_for_server(self):
        if not self._wait_for_server():
            self.after(1000, self.wait_for_server)

    def on_close(self):
        self.on_stop()
        self.quit()

    def on_select_path(self):
        new_dir = filedialog.askdirectory(**self.dir_opt)
        if new_dir and self._check_cactus_dir(new_dir):
            self.web_dir = new_dir
        self.selected_path.set(self.web_dir)

    def _alert(self, message):
        messagebox.showinfo('Warning', message)


def main():
    set_start_method('forkserver')
    root = tk.Tk()
    app = GuiApplication(root, title='Crate Cactus')
    app.pack(side='top', fill='both', expand=True)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()
        root.destroy()

