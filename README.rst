============
crate-cactus
============

Build system for `crate.io`_ website.

It uses the static website generator tool Cactus_ to generate HTML pages.


Development Setup
=================

System requirements::

    libjpeg, zlib, libpng

Clone repo and update submodules::

    git clone git@github.com:crate/crate-cactus.git
    cd crate-cactus
    git submodule update --init

The dev environment requires ``Python 3 (<=3.4)`` to be installed::

    python3.4 bootstrap.py
    bin/buildout -N

To start the development server::

    bin/serve

By default Cactus serves the site on port ``8000``.
You can specify a specific port with the ``--port`` argument::

    bin/serve --port 8888

Incremental Builds
------------------

You can enable support for 'incremental' builds by using the ``-i`` argument::

    bin/serve -i

In this mode Cactus will only re-build files that actually changed while editing.

Custom Build Path
------------------

Using the ``--path`` argument, you can specify a different site path than ``.``::

    bin/serve --path /path/to/cactus/site

Running Tests
=============

You can run the test suite with::

    bin/test

Crate Cactus GUI/CLI
====================

Starting the GUI requires Python with Tcl/Tk support (tkinter).
The run::

    bin/cactus_gui

For the CLI::

    bin/cactus_cli --site=/path/to/cactus-site

This will start 2 processes, one for the build/webserver and one for the image
resizing.


Site Content
============

All pages are located in the ``crate-web`` submodule located in ``site/``
and respective subfolders. To edit content, use the `crate/crate-web`_
repository.


Deployment
==========

Deploy Staging
--------------

Run the `deploy_web-staging`_ job on Jenkins.

You can build manually using ``buildout-production.cfg``::

    $ bin/buildout -c buildout-production.cfg
    $ bin/cactus build --path site --conf config/staging.json

Deploy Production
-----------------

Run the `deploy_web-production`_ job on Jenkins.

You can build manually using ``buildout-production.cfg``::

    $ bin/buildout -c buildout-production.cfg
    $ bin/cactus build --path site --conf config/production.json


.. _`crate.io`: https://crate.io
.. _`Cactus`: https://github.com/koenbok/Cactus
.. _`crate/crate-web`: https://github.com/crate/crate-web
.. _`deploy_web-staging`: https://jenkins.crate.io/job/deploy_web-staging/
.. _`deploy_web-production`: https://jenkins.crate.io/job/deploy_web-production/
