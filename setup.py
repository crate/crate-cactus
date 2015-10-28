# -*- coding: utf-8; -*-
# vi: set encoding=utf-8

# Licensed to CRATE Technology GmbH ("Crate") under one or more contributor
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
import re
import sys
from setuptools import setup, find_packages

requirements = [
    'setuptools',
    'Cactus==3.3.2p1',
    'Pillow',
#    'cdn-fastly',
    'watchdog',
]

if (2, 6) == sys.version_info[:2]:
    requirements.append('argparse>=1.1')

def read(path):
    return open(os.path.join(os.path.dirname(__file__), path)).read()

setup(
    name='crate-cactus',
    version='0.1.0',
    url='https://github.com/crate/crate-cactus',
    author='CRATE Technology GmbH',
    author_email='office@crate.io',
    package_dir={'': 'src'},
    description='Crate Cactus',
    long_description=read('README.rst'),
    platforms=['any'],
    license='Apache License 2.0',
    keywords='',
    packages=find_packages('src'),
    dependency_links=[
      'http://download.crate.io/eggs/',
    ],
    namespace_packages=[],
    entry_points={
        'console_scripts': [
#            'cactus=cactus.cli:cli_entrypoint',
            'resize_images=web.resize:main',
            'run=web.gui:main',
        ]
    },
    extras_require=dict(
        argcompletion=['argcomplete']
    ),
    install_requires=requirements
)
