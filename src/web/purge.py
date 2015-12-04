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

import sys
import fastly
from argparse import ArgumentParser


def purge(api_key, service_key, purge_key):
    api = fastly.connect(api_key)
    print(api.purge_service_by_key(service_key, purge_key))


if __name__ == '__main__':
    """
    Usage: python purge.py --api-key <KEY>
    """
    parser = ArgumentParser(description='purge fastly')
    parser.add_argument('--api-key', type=str, help='Fastly API key')
    parser.add_argument('--service-key', type=str, help='Fastly Service key', default='1bUC7xOWcgbVWpBPqPqHp')
    parser.add_argument('--purge-key', type=str, help='Purge key', default='web')
    args = parser.parse_args()
    purge(args.api_key)

