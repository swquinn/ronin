# Copyright (c) 2015 Sean Quinn
#
# Licensed under the MIT License (http://opensource.org/licenses/MIT)
#
# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pprint import pprint
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
import glob
import logging

#: The logging apparatus
logger = logging.getLogger(__name__)


class RoninEventHandler(PatternMatchingEventHandler):
    """
    A Watchdog file system event handler for performing file synchronization
    based on the file synchronization strategy.
    """

    def __init__(self, ronin=None):
        super_init = super(RoninEventHandler, self).__init__
        super_init()

        #: Reference to the ronin process that informs this file system
        #: event handler how it should act when an event occurs.
        self.ronin = ronin

        #: Attribute strategy exclude patterns to the ignore patterns of the
        #: event handler.
        strategy = self.ronin.strategy
        self._ignore_patterns = strategy.exclude_patterns
        logger.debug(self._ignore_patterns)

    def on_any_event(self, event):
        super(RoninEventHandler, self).on_any_event(event)
        logger.debug("Received file system event: %s", event)

        try:
            strategy = self.ronin.strategy
            strategy.invoke()
        except Exception as err:
            logger.error("An unexpected error occurred while synchronizing files: {0}".format(err.message))
            logger.exception(err)
