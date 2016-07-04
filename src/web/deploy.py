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

import fastly
from argparse import ArgumentParser
from purge_rtd import rebuild_all


def purge_fastly(args):
    api = fastly.connect(args.api_key)
    print(api.purge_service_by_key(args.service_key, args.purge_key))


def main():
    parser = ArgumentParser(description='Deploy tools for Crate.IO website')
    subparsers = parser.add_subparsers()

    parser_purge = subparsers.add_parser('purge-fastly',
                                         help='Purge fastly caches')
    parser_purge.add_argument('--api-key', type=str,
                              help='Fastly API key',
                              required=True)
    parser_purge.add_argument('--service-key', type=str,
                              help='Fastly Service key',
                              required=True)
    parser_purge.add_argument('--purge-key', type=str,
                              help='Purge key',
                              default='web')
    parser_purge.set_defaults(func=purge_fastly)

    parser_rtd = subparsers.add_parser('rebuild-rtd',
                                       help='Rebuild all projects on RTD')
    parser_rtd.add_argument('user', type=str)
    parser_rtd.add_argument('password', type=str)
    parser_rtd.set_defaults(func=rebuild_all)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
