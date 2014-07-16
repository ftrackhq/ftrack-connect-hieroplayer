# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from __future__ import absolute_import

from ._version import __version__

# Setup logging for ftrack.
# TODO: Check with The Foundry if there is any better way to customise logging.
from . import logging
logging.setup()


# Import remaining modules and instantiate ftrack plugin.
from .plugin import Plugin as _Plugin
plugin = _Plugin()