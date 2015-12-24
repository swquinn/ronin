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

from . import FileSyncStrategy
from pprint import pprint
import logging
import os
import subprocess

#: The logging apparatus.
logger = logging.getLogger(__name__)


class RsyncStrategy(FileSyncStrategy):
    """
    """

    def get_args(self):
        """
        """
        manifest = self.manifest
        args = list()

        #: Append all of the arguments specified in the manifest file to
        #: the list of arguments that the rsync handler will use.
        for arg in manifest.args:
            args.append(str(arg))

        #:
        for exclusion in manifest.exclude:
            args.append("--exclude="+str(exclusion))
        args.append(self.source)
        args.append(self.target)
        return args

    def invoke(self):
        command = list(["rsync"])
        if self.manifest.elevate:
            command.insert(0, "sudo")
        command = command + self.get_args()
        logger.debug("Running command: {0}".format(" ".join(command)))
        return subprocess.call(command)
