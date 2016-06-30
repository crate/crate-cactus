# -*- coding: utf-8; -*-
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

import slumber
import requests
import logging

RTD_BASE = 'https://readthedocs.org'
login_url = RTD_BASE + '/accounts/login/'
wipe_url = RTD_BASE + '/wipe/{}/{}/'
build_url = RTD_BASE + '/build/{}'

projects = [
    "crash",
    "crate",
    "crate-dbal",
    "crate-java",
    "crate-jdbc",
    "crate-pdo",
    "crate-python"
]


logging.basicConfig()
logger = logging.getLogger('purge')
logger.setLevel(logging.DEBUG)


def rebuild_project(project_slug, session, api):
    offset = 0
    limit = 50
    while True:
        objects = api.version(project_slug).get(limit=limit, offset=offset)['objects']
        for obj in objects:
            project_id = obj['project']['id']
            if obj.get('built', False):
                logger.info("Wiping: {}".format(obj['slug']))
                res = session.post(wipe_url.format(project_slug, obj['slug']))
                status = res.status_code
                if status == 200:
                    logger.info("Building: {}...".format(obj['slug']))
                    res = session.post(build_url.format(project_id), data={"version_slug": obj['slug']})
                    status = res.status_code
                if status != 200:
                    logger.error("An error occured while rebuilding: \n {}".format(res))
        if len(objects) < limit:
            break
        offset += limit


def login(user, password):
    session = requests.Session()
    session.get(login_url)

    token = session.cookies.get('csrftoken')

    data = {"csrfmiddlewaretoken": token, "login": user, "password": password}
    session.post(login_url, data=data, headers={"referer": login_url})
    api = slumber.API(base_url='http://readthedocs.org/api/v1/', auth=(user, password))
    return session, api


def rebuild_all(args):
    session, api = login(args.user, args.password)
    for project in projects:
        logger.info("Purge: {}\n".format(project))
        rebuild_project(project, session, api)

