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
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

from collection import Collection

from cactus.config.file import ConfigFile
from cactus.page import Page
from cactus.site import Site

import django.conf


class CollectionsPluginTest(unittest.TestCase):

    def setUp(self):
        self.clear_django_settings()
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, "test")
        os.mkdir(self.path)
        for dir in ['pages', 'static', 'templates', 'plugins']:
            os.mkdir(os.path.join(self.path, dir))

        conf_path = os.path.join(self.path, "config.json")
        self.conf_file = ConfigFile(conf_path)
        self.conf_file.set("collections", {})
        self.conf_file.write()

        for dir in ['blog', 'articles', 'docs']:
            now = datetime.now()
            path = os.path.join(self.path, 'pages', dir)
            os.mkdir(path)
            for i in range(1, 4):
                date = now + timedelta(hours=i)
                with open(os.path.join(path, 'page-{0}.html'.format(i)), 'w') as fp:
                    fp.write('title: {0} {1}\n'.format(dir, i))
                    fp.write('created: {0:%Y-%m-%dT%H:%M}\n'.format(date))
                    fp.write('\n')
                    fp.write('# Hello World\n')

            if dir == 'docs':
                with open(os.path.join(path, 'toc'), 'w') as fp:
                    fp.write('docs/page-2.html\n')
                    fp.write('docs/page-3.html\n')
                    fp.write('docs/page-1.html\n')

        self.site = Site(path=self.path, config_paths=conf_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        self.clear_django_settings()

    def clear_django_settings(self):
        django.conf.settings._wrapped = django.conf.empty

    def test_init(self):
        coll = Collection('Articles', 'a/', 'article.html')
        self.assertEquals('<Articles: a/ (0 pages)>', coll.__repr__())
        self.assertEquals('Articles', coll.title)
        self.assertEquals('a/', coll.path)
        self.assertEquals('article.html', coll.template)
        self.assertEquals([], coll.pages)

    def test_page_filter(self):
        pages = [
            Page(self.site, 'articles/page-1.html'),
            Page(self.site, 'blog/page-1.html'),
        ]
        for path in ['articles/', 'blog/']:
            coll = Collection('Collection', path, 'template.html', pages=pages)
            self.assertEquals(1, len(coll.pages))
            self.assertEquals(1, len(coll))
            for page in coll.pages:
                self.assertTrue(page['path'].startswith(path))

    def test_contains_page(self):
        pages = [
            Page(self.site, 'blog/page-1.html'),
            Page(self.site, 'blog/page-2.html'),
            Page(self.site, 'blog/page-3.html'),
        ]
        other_page = Page(self.site, 'blog/page-4.html')
        coll = Collection('Collection', 'blog/', 'template.html', pages=pages)
        coll.sort('date', reverse=True)

        self.assertEquals(['blog/page-3.html', 'blog/page-2.html', 'blog/page-1.html'],
                          [p['path'] for p in coll.pages])

        self.assertTrue(coll.contains_page(pages[0]))
        self.assertFalse(coll.contains_page(other_page))

        page_ctx = coll.page_context(pages[0])
        self.assertEquals('blog/page-1.html', page_ctx['path'])

        with self.assertRaises(ValueError) as cm:
            page_ctx = coll.page_context(other_page)
        self.assertEquals("'blog/page-4.html' is not in list", str(cm.exception))

    def test_navigation(self):
        pages = [
            Page(self.site, 'blog/page-1.html'),
            Page(self.site, 'blog/page-2.html'),
            Page(self.site, 'blog/page-3.html'),
        ]
        coll = Collection('Collection', 'blog/', 'template.html', pages=pages)
        coll.sort('date', reverse=False)
        coll.create_navigation()

        self.assertEquals('blog/page-2.html', coll[0]['prev_post']['path'])
        self.assertEquals('blog/page-3.html', coll[1]['prev_post']['path'])

        self.assertEquals('blog/page-2.html', coll[2]['next_post']['path'])
        self.assertEquals('blog/page-1.html', coll[1]['next_post']['path'])

    def test_sortbytoc(self):
        pages = [
            Page(self.site, 'docs/page-1.html'),
            Page(self.site, 'docs/page-2.html'),
            Page(self.site, 'docs/page-3.html')
        ]
        coll = Collection('Collection', 'docs/', 'docs.html', pages=pages)
        coll.sort(toc=os.path.join(self.path, 'pages', 'docs', 'toc'))

        self.assertEquals(['docs/page-2.html', 'docs/page-3.html', 'docs/page-1.html'],
                          [p['path'] for p in coll.pages])


    def test_preBuild(self):
        # TODO: test preBuild method
        pass

    def test_preBuildPage(self):
        # TODO: test preBuildPage method
        pass


