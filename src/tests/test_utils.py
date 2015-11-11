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


import unittest
from web import utils
from datetime import datetime, date
import django.conf

class UtilsTest(unittest.TestCase):

    def setUp(self):
        django.conf.settings._wrapped = django.conf.empty
        if not django.conf.settings.configured:
            django.conf.settings.configure()

    def tearDown(self):
        django.conf.settings._wrapped = django.conf.empty

    def test_toDict(self):
        a_post = {
            'title': 'some-title',
            'date': 'a-date',
            'category': 'category',
            'url': '/post/1',
            'raw_body': 'short body',
            'author': 'someone',
            'tags': ['tags', 'tags2'],
            'topics': ['crate'],
        }

        expected_a_post = {
            "id": "4034c5bce7dad3b40247b6c812b0c93c",
            "title": "some-title",
            "date": "a-date",
            'tags': ['tags', 'tags2'],
            'topics': ['crate'],
            "category": "category",
            "permalink": "/post/1",
            "content": '',
            "excerpt": "short body",
            "author": "someone"
        }
        body_26w = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam a tellus euismod, congue est nec, egestas diam. Phasellus sed sollicitudin lacus. Etiam rhoncus, nulla a convallis"

        md_body = "# HELLO WORLD"

        settings = {"site": "https://crate.io"}

        self.assertEqual(utils.toDict({}, []), [])
        self.assertEqual(utils.toDict({}, None), [])
        self.assertEqual(utils.toDict(None, None), [])

        # expected output
        self.assertEqual(utils.toDict({}, [a_post]), [expected_a_post])

        # no unique checks
        self.assertEqual(utils.toDict({}, [a_post] * 3), [expected_a_post] * 3)

        # excerpts are truncated
        truncated_excerpt = utils.toDict({}, [dict(a_post, raw_body = body_26w)])[0]

        self.assertEqual(len(truncated_excerpt["excerpt"].split(" ")), len(body_26w.split(" ")) - 1)

        # excerpts can contain markdown, but is stripped of its tags
        md_excerpt = utils.toDict({}, [dict(a_post, raw_body = md_body)])[0]
        self.assertEqual(md_excerpt["excerpt"], "HELLO WORLD")

        # permalinks are prepended if a settings have a site key
        permalink = utils.toDict(settings, [a_post])[0]
        self.assertEqual(permalink["permalink"], '{0}{1}'.format(settings["site"], a_post["url"]))


    def test_parseDate(self):

        self.assertEqual(type(utils.parseDate()), type(datetime.now()))
        self.assertEqual(type(utils.parseDate(None)), type(datetime.now()))

        fb = datetime.now()
        self.assertIs(utils.parseDate(None, fallback = fb), fb)
        self.assertIs(utils.parseDate(fallback = fb), fb)

        date_only =  datetime(1234, 1, 22)
        dt_no_secs = datetime(1234, 1, 22, 13, 33)
        full_dt = datetime(1234, 1, 22, 13, 33, 37)

        # proper formatting
        self.assertEqual(utils.parseDate("{:%Y-%m-%d}".format(date_only)), date_only)
        self.assertEqual(utils.parseDate("{:%Y/%m/%d %H:%M:%S}".format(full_dt)), full_dt)
        self.assertEqual(utils.parseDate("{:%Y-%m-%dT%H:%M}".format(dt_no_secs)), dt_no_secs)


        # fallback is only used as a fallback
        self.assertIsNot(utils.parseDate("{:%Y-%m-%d}".format(date_only), fallback = fb), fb)

        # improper formatting
        self.assertIs(utils.parseDate("asdf", fallback = fb), fb)
        self.assertIs(utils.parseDate("", fallback = fb), fb)
        self.assertIs(utils.parseDate("12-12-12", fallback = fb), fb)

        # curious cases
        self.assertEqual(utils.parseDate("0012-12-12", fallback = fb), datetime(12, 12, 12))
        self.assertEqual(utils.parseDate("1200-12-12", fallback = fb), datetime(1200, 12, 12))

        with self.assertRaises(ValueError):
            utils.parseDate("0000-99-99")

    def test_parsePost(self):

        with self.assertRaises(TypeError):
            utils.parsePost({})
            utils.parsePost(None)

        body = "this is an article about testing"
        self.assertIsInstance(utils.parsePost("post"), type(()))

        self.assertEqual(utils.parsePost("""hello: world\n\n{}""".format(body)), ({"hello": "world"}, body))

        self.assertEqual(utils.parsePost("""hello: world\n{}""".format(body)), ({"hello": "world"}, ''))

        self.assertEqual(utils.parsePost("""\n{}\nhello:world""".format(body)), ({}, 'this is an article about testing\nhello:world'))
