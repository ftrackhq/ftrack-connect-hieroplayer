=====================================
******* DEPRECATED REPOSITORY *******
=====================================
This repository has reached its EOL and has been deprecated and will be publicly removed in September 2023. Users will still be able to download the latest version under demand by sending a request message to support@ftrack.com.

We highly encourage our users to use the new integrations framework which supports the latest versions of the most used DCC and is much easier to customize and extend.
You can find the latest downloadable version of the framework in the plugin manager of ftrack connect https://go.ftrack.com/connect-download.

Framework documentation: https://ftrackhq.github.io/integrations/libs/framework-core/

All our maintained code is now under a monorepo repository that as of the date of this message (26/05/2023) is still private as we are still doing some migration and setup jobs. We are working hard to open it publicly as soon as we can. You will be able to find the monorepo at: https://github.com/ftrackhq/integrations.

Don't hesitate on contact our support team if you have any inquiries: support@ftrack.com


###########################
ftrack connect hiero player
###########################

ftrack connect review plugin for The Foundry's HIEROPLAYER.

************
Installation
************

.. highlight:: bash

You can clone the public repository::

    $ git clone git@bitbucket.org:ftrack/ftrack-connect-hieroplayer.git

Or download the
`zipball <https://bitbucket.org/ftrack/ftrack-connect-hieroplayer/get/master.zip>`_

Once you have a copy of the repository, copy the contents of the *source* folder
into the *Python/Startup* plugin folder for HIEROPLAYER. To find out where the
plugin folder is on your system consult the `The Foundry developer documentation
<http://docs.thefoundry.co.uk/products/hiero/developers/1.8/hieropythondevguide/setup.html>`_.

Dependencies
============

* ftrack Python API (Download from your ftrack server and make available on
  ``PYTHONPATH``)
* `Hiero Player or Hiero <http://www.thefoundry.co.uk/products/hiero-product-family>`_

*************
Documentation
*************

Full documentation can be found at https://ftrack-connect-hieroplayer.readthedocs.io/en/latest/

*********************
Copyright and license
*********************

Copyright (c) 2014 ftrack

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License in the LICENSE.txt file, or at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.