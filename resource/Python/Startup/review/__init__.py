# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from __future__ import absolute_import

# Setup logging for ftrack.
# TODO: Check with The Foundry if there is any better way to customise logging.
from . import logging as _logging
_logging.setup()

import hiero


if hiero.core.env.get('VersionMajor') <= 10:
	# Import remaining modules and instantiate ftrack plugin.
	from .plugin import Plugin as _Plugin
	plugin = _Plugin()
else:
	import logging
	logging.error('Not supported yet on nuke 11.')