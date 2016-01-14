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

import logging
import os

#: The logging apparatus.
logger = logging.getLogger(__name__)


class FileSyncStrategy(object):
    """
    The base class for all file sync handlers.
    """

    def __init__(self, source, target, manifest):
        #: The manifest
        self.manifest = manifest

        #: The source directory that this sync handler will copy files from.
        if os.path.isfile(source):
            source = os.path.dirname(source)
        self.source = os.path.abspath(os.path.expanduser(source)) + os.sep

        #: The target directory that this sync handler will copy files to.
        self.target = os.path.abspath(os.path.expanduser(target))

    @property
    def exclude_paths(self):
        exclude_paths = list()
        for exclusion in self.manifest.exclude:
            path = os.path.abspath(os.path.join(".", exclusion))
            exclude_paths.append(path)
        return exclude_paths

    @property
    def exclude_patterns(self):
        exclude_paths = self.exclude_paths
        for path in exclude_paths:
            if os.path.isdir(path):
                pattern = os.path.join(path, "*")
                exclude_paths.append(pattern)
        return exclude_paths

    def invoke(self):
        """
        Handle file synchronization based on the instructions in the
        manifest from the source directory to the target directory.
        """
        raise NotImplementedError()


class StrategyFactory(object):
    """
    Factory object for initializing and returning sync handlers for the
    supported type defined within a manifest.
    """

    def get_strategy(self, source, manifest):
        """
        Return a file sync handler for the given type defined within the
        manifest, operating on the source and target directories.

        :param source: the source directory where files will be copied from.
        :param manigest: the manifest containing all other configuration for
            the sync handler.
        """
        strategy_type = manifest.type
        path = manifest.path
        if strategy_type == "rsync":
            from .rsync import RsyncStrategy
            return RsyncStrategy(source, path, manifest)
        else:
            raise ValueError("Unknown type: {0}".format(strategy_type))
