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

__docformat__ = "reStructuredText"

import os
import sys
import time
import logging

from PIL import Image
from argparse import ArgumentParser
from colorlog import ColoredFormatter
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler


logging.basicConfig()
logger = logging.getLogger('resize')
logger.setLevel(logging.DEBUG)


class ImageProcessor():

    sizes = [1024, 800, 600, 200]

    def __init__(self, inputFile):
        self.filepath = os.path.abspath(inputFile)
        self.dirname = os.path.dirname(self.filepath)
        self.filename = os.path.splitext(os.path.basename(self.filepath))[0]
        self.file_ext = os.path.splitext(inputFile)[1]

    def _out_file_path(self, size):
        return os.path.join(self.dirname,
                            '{0}_{1}{2}'.format(self.filename,
                                                str(size),
                                                self.file_ext))

    def resize(self):
        for size in self.sizes:
            self._resize(size)

    def _resize(self, size):
        logger.debug('Resizing image {0} to {1}px ...'.format(self.filepath, size))
        try:
            img = Image.open(self.filepath)
            # max-width, max-height
            img.thumbnail((size, size))
            img.save(self._out_file_path(size))
        except IOError:
            logger.error("Could not convert file {0}".format(self.filepath))


class FileHandler(RegexMatchingEventHandler):

    def process(self, event):
        image = ImageProcessor(event.src_path)
        image.resize()

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


def parse_args(args):
    pwd = os.path.abspath(os.path.join(os.getcwd(), 'site'))
    parser = ArgumentParser(description='Image resize daemon')
    parser.add_argument('-d', '--dir', type=str, default=pwd,
                        help='directory to watch')
    return parser.parse_args(args)


def resize(args):
    _ = parse_args(args)
    observer = Observer()

    image_ext = ["jpg", "jpeg", "png", "tif", "tiff", "gif"]
    regexes = []

    for ext in image_ext:
        regexes.append(".*." + ext)

    ignore_regexes = [".*(_[0-9]+).(.+)"]

    observer.schedule(FileHandler(regexes=regexes, ignore_regexes=ignore_regexes),
                      _.dir, recursive=True)
    observer.start()
    logger.info('Watching for images in directory {0}'.format(_.dir))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

def main():
    resize(sys.argv[1:])
