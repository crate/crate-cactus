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

import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from PIL import Image

class ImageProcessor():
    
    def __init__(self, inputFile):
        self.filepath = os.path.abspath(inputFile)
        self.dirname = os.path.dirname(self.filepath)
        self.filename = os.path.splitext(os.path.basename(self.filepath))[0]
        self.fileExt = os.path.splitext(inputFile)[1]
    
    def resize(self, width, height):
        try:
            im = Image.open(self.filepath)
            # max-width, max-height
            im.thumbnail((width, height))
            outfile = '{0}/{1}_{2}{3}'.format(self.dirname, self.filename, str(im.size[0]), self.fileExt)
            im.save(outfile)
        except IOError:
            print("cannot convert", self.filepath)

class FileHandler(RegexMatchingEventHandler):

    def process(self, event):
        image = ImageProcessor(event.src_path)
        image.resize(800, 800)
        image.resize(600, 600)
        image.resize(200, 200)
    
    def on_modified(self, event):
        self.process(event)
    
    def on_created(self, event):
        self.process(event)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    observer = Observer()
    
    fileExts = ["jpg", "jpeg", "png", "tif", "tiff", "gif"]
    regexes = []
        
    for ext in fileExts:
        regexes.append(".*." + ext)
    
    ignore_regexes = [".*(_[0-9]+).(.+)"]
    
    observer.schedule(FileHandler(regexes=regexes, ignore_regexes=ignore_regexes), path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()

if __name__ == '__main__':
    main()
