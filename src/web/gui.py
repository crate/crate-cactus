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
import sys
import time
import logging
import subprocess
import urllib.request
from logging.handlers import SysLogHandler
from multiprocessing import Process, Pipe, freeze_support

from cactus.cli import main as cmd_cactus
from web.resize import resize as cmd_resize

# ensure Python 2 compatibility
set_start_method = lambda x: None

if (3, 0) <= sys.version_info[:2]:
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from multiprocessing import set_start_method
else:
    import Tkinter as tk
    try:
        from Tkinter import filedialog
        from Tkinter import messagebox
    except ImportError:
        import tkFileDialog as filedialog
        import tkMessageBox as messagebox


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(SysLogHandler('/var/run/syslog'))


class BackgroundProcess(Process):

    def __init__(self, site_path, *args, **kwargs):
        super(BackgroundProcess, self).__init__(*args, **kwargs)
        self.site_path = site_path
        self.daemon = True


class WebserverProcess(BackgroundProcess):

    def run(self, *args):
        cmd_cactus(['serve',
                    '-i',
                    '--path', self.site_path,
                    '--config', os.path.join(self.site_path, 'config.json')])


class ResizeProcess(BackgroundProcess):

    def run(self, *args):
        cmd_resize(['-d', os.path.join(self.site_path, 'static')])


class Application(tk.Frame):

    _cactus = None
    _resize = None

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
        self._running = running
        self.btn_start_stop["text"] = self._running and "Stop" or "Start"
        self.status.set(self._running and 'Running ...' or 'Stopped')

    def on_start_stop(self):
        if self._running:
            self.status.set('Stopping ...')
            self.on_stop()
        elif self._check_cactus_dir(self.web_dir):
            self.status.set('Starting ...')
            self.on_start()

    def on_start(self):
        site_path = self.selected_path.get()
        # start Cactus in new thread
        if not self._cactus:
            LOGGER.info('Starting Cactus server ...')
            self._cactus = WebserverProcess(site_path)
            self._cactus.start()
        else:
            LOGGER.warn('Cactus server already running.')
        # start resize daemon in new thread
        if not self._resize:
            LOGGER.info('Starting resize daemon ...')
            self._resize = ResizeProcess(site_path)
            self._resize.start()
        else:
            LOGGER.warn('Resize daemon already running.')
        self._wait()

    def _wait(self, time_slept=0.0):
        url = 'http://localhost:8000'
        try:
            req = urllib.request.Request(url=url, method='HEAD')
            with urllib.request.urlopen(req) as resp:
                if resp.status == 200:
                    self._set_running(True)
                    subprocess.Popen(['open', url])
                    return
        except Exception as e:
            LOGGER.debug('Waiting for webserver ... {0:.1f}s'.format(time_slept))
            if time_slept > 30.0:
                self.on_stop()
                return
        self.after(1000, self._wait, time_slept+1.0)

    def on_stop(self):
        if self._cactus and self._cactus.is_alive():
            LOGGER.info('Stopping Cactus server ...')
            self._cactus.terminate()
            LOGGER.info('Stopped')
        else:
            LOGGER.info('Cactus server not running.')
        self._cactus = None
        if self._resize and self._resize.is_alive():
            LOGGER.info('Stopping resize daemon ...')
            self._resize.terminate()
            LOGGER.info('Stopped')
        else:
            LOGGER.info('Resize daemon not running.')
        self._resize = None
        self._set_running(False)

    def on_close(self):
        self.on_stop()
        self.quit()

    def on_select_path(self):
        new_dir = filedialog.askdirectory(**self.dir_opt)
        if new_dir and self._check_cactus_dir(new_dir):
            self.web_dir = new_dir
        self.selected_path.set(self.web_dir)
        LOGGER.info('Selected site: {0}'.format(self.web_dir))

    def _check_cactus_dir(self, site_path):
        conf = os.path.join(site_path, 'config.json')
        pages = os.path.join(site_path, 'pages')
        if os.path.exists(conf) and \
           os.path.isfile(conf) and \
           os.path.exists(pages) and \
           os.path.isdir(pages):
            return True
        else:
            error_msg = '{0} is not a valid Cactus site'.format(site_path)
            messagebox.showinfo('Warning', error_msg)
            return False


def build_app():
    set_start_method('forkserver')
    root = tk.Tk()
    app = Application(root, title='Crate Cactus')
    app.pack(side='top', fill='both', expand=True)
    return root


def main():
    # Entry point for CLI
    root = build_app()
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()
        root.destroy()
    finally:
        sys.exit(0)


if __name__ == '__main__':
    # Entry point for app bundle
    root = build_app()
    root.mainloop()

