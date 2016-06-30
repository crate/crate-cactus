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
import time
import logging
import requests
from multiprocessing import Process

from cactus.cli import main as cmd_cactus
from web.resize import resize as cmd_resize

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BackgroundProcess(Process):

    def __init__(self, site_path, *args, **kwargs):
        super(BackgroundProcess, self).__init__(*args, **kwargs)
        self.site_path = site_path


class WebserverProcess(BackgroundProcess):

    def run(self, *args):
        cmd_cactus(['serve',
                    '-i',
                    '--path', self.site_path,
                    '--config', os.path.join(self.site_path, 'config.json')])


class ResizeProcess(BackgroundProcess):

    def run(self, *args):
        cmd_resize(['-d', os.path.join(self.site_path, 'static')])


class Application(object):

    _cactus = None
    _resize = None

    def __init__(self):
        self._running = False

    def _set_running(self, running):
        self._running = running

    def on_start(self):
        is_site = self._check_cactus_dir(self.web_dir)
        if not is_site or self._running:
            return
        # start Cactus in new thread
        if not self._cactus:
            LOGGER.info('Starting Cactus server ...')
            self._cactus = WebserverProcess(self.web_dir)
            self._cactus.start()
        else:
            LOGGER.warn('Cactus server already running.')
        # start resize daemon in new thread
        if not self._resize:
            LOGGER.info('Starting resize daemon ...')
            self._resize = ResizeProcess(self.web_dir)
            self._resize.start()
        else:
            LOGGER.warn('Resize daemon already running.')
        self.wait_for_server()

    def wait_for_server(self):
        time_waited = 0.0
        while not self._wait_for_server():
            if time_waited < 30.0:
                time_waited += 1.0
                time.sleep(1.0)
            else:
                self.on_stop()
                break

    def _wait_for_server(self):
        try:
            resp = requests.head(url='http://localhost:8000/robots.txt')
        except Exception as e:
            LOGGER.debug('Waiting for webserver ...')
            return False
        else:
            running = resp.status_code == 200
            self._set_running(running)
            return running

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

    def _check_cactus_dir(self, site_path):
        conf = os.path.join(site_path, 'config.json')
        pages = os.path.join(site_path, 'pages')
        if os.path.exists(conf) and \
           os.path.isfile(conf) and \
           os.path.exists(pages) and \
           os.path.isdir(pages):
            return True
        else:
            LOGGER.error('{0} is not a valid Cactus site'.format(site_path))
            return False

    def wait_for_processes(self):
        if self._cactus and self._resize:
            return [p.join() for p in (self._cactus, self._resize)]
        else:
            self.on_stop()
            return [1, 1]

