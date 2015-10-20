============
crate-cactus
============

Build system for `crate.io`_ website.

It uses the static website generator tool [Cactus](https://github.com/koenbok/Cactus)
to generate HTML pages.


Development Setup
=================

Clone repo and update submodules::

    $ git clone git@github.com:crate/crate-cactus.git
    $ cd crate-cactus
    $ git submodule update --init

The dev environment requires Python 2.7 to be installed::

    $ python2.7 bootstrap.py
    $ bin/buildout -N

Select an environment::

    $ bin/env local

Other options are: ``staging`` and ``production``.


To start the development server::

    $ bin/serve

By default Cactus serves the site on port ``8000``.
You can specify a specific port with the ``--port`` argument::

    $ bin/serve --port 8888

You can enable support for 'incremental' builds by using the ``-i`` argument::

    $ bin/serve -i

In this mode Cactus will only re-build files that actually changed while editing.


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

Deploy Production
-----------------

Run the `deploy_web-production`_ job on Jenkins.



.. _`crate.io`: https://crate.io
.. _`crate/crate-web`: https://github.com/crate/crate-web
.. _`deploy_web-staging`: https://jenkins.crate.io/job/deploy_web-staging/
.. _`deploy_web-production`: https://jenkins.crate.io/job/deploy_web-production/
