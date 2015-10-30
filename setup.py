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
__version__ = (0, 1, 0)

import os
import sys
from setuptools import setup, find_packages


root_dir = os.path.dirname(__file__)

requirements = [
    'setuptools',
    'Pillow',
    'watchdog',
]

with open(os.path.join(root_dir, 'cactus', 'requirements.txt')) as fp:
    requirements += [l.rstrip('\n') for l in fp.readlines()]

def read(path):
    return open(os.path.join(os.path.dirname(__file__), path)).read()

kwargs = dict(
    name = 'crate-cactus',
    version = '.'.join([str(x) for x in __version__]),
    url = 'https://github.com/crate/crate-cactus',
    author = 'CRATE Technology GmbH',
    author_email = 'office@crate.io',
    package_dir = {'': 'src', 'cactus': 'cactus/cactus'},
    description = 'Cactus Website Deploy Tool',
    long_description = read('README.rst'),
    platforms = ['any'],
    license = 'Apache License 2.0',
    packages = find_packages('src') + find_packages('cactus'),
    namespace_packages = [],
    entry_points = {
        'console_scripts': [
            'cactus=cactus.cli:cli_entrypoint',
            'resize_images=web.resize:main',
            'cactus_gui=web.gui:main',
        ]
    },
    install_requires = requirements,
    setup_requires = ["py2app"],
)

try:
    import py2app
except ImportError:
    # py2app is not present
    # GUI cannot be built as standalone application
    pass
else:
    kwargs.update(dict(
        options = dict(
            py2app = dict(
                iconfile = os.path.join('resources', 'Icons.icns'),
                plist = os.path.join('resources', 'Info.plist'),
                # fix dynamic imports
                packages = [
                    'web',
                    'cactus',
                    'django',
                    'django_markwhat',
                    'keyring',
                ],
                argv_emulation = 1,
            ),
        ),
        app = [
            os.path.join('src','web','gui.py'),
        ],
    ))
    from pprint import pprint
    pprint(kwargs)

setup(**kwargs)

