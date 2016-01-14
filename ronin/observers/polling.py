#!/usr/bin/env python
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


"""
:module: ronin.observers.polling
:synopsis: Discriminated polling emitter and observer implementations.

Classes
-------
.. autoclass:: DiscriminatedPollingObserver
   :members:
   :show-inheritance:
"""

from watchdog.utils import stat as default_stat
from ronin.utils.dirsnapshot import DiscriminatedDirectorySnapshot
from watchdog.utils.dirsnapshot import DirectorySnapshotDiff
from watchdog.observers.api import (
    BaseObserver,
    ObservedWatch,
    DEFAULT_OBSERVER_TIMEOUT,
    DEFAULT_EMITTER_TIMEOUT
)
from watchdog.observers.polling import PollingEmitter
import logging
import os

logger = logging.getLogger(__name__)


class DiscriminatedPollingEmitter(PollingEmitter):
    """
    Platform-independent emitter that polls a directory to detect file
    system changes.
    """

    def __init__(self, event_queue, watch,
                 exclude_paths=None,
                 timeout=DEFAULT_EMITTER_TIMEOUT,
                 stat=default_stat,
                 listdir=os.listdir):
        PollingEmitter.__init__(self, event_queue, watch, timeout, stat, listdir)
        self._exclude_paths = exclude_paths
        self._take_snapshot = lambda: DiscriminatedDirectorySnapshot(
            self.watch.path, self.watch.is_recursive, ignore_paths=self._exclude_paths, stat=stat, listdir=listdir)


class DiscriminatedPollingObserver(BaseObserver):
    """
    Platform-independent observer that polls a directory to detect file
    system changes.
    """

    def __init__(self, timeout=DEFAULT_OBSERVER_TIMEOUT):
        BaseObserver.__init__(self, emitter_class=DiscriminatedPollingEmitter, timeout=timeout)

    def schedule(self, event_handler, path, exclude_paths=None, recursive=False):
        """
        Schedules watching a path and calls appropriate methods specified
        in the given event handler in response to file system events.

        :param event_handler:
            An event handler instance that has appropriate event handling
            methods which will be called by the observer in response to
            file system events.
        :type event_handler:
            :class:`watchdog.events.FileSystemEventHandler` or a subclass
        :param path:
            Directory path that will be monitored.
        :type path:
            ``str``
        :param exclude_paths:
            The paths that will be omitted from file change observations.
        :type exclude_paths:
            ``list``
        :param recursive:
            ``True`` if events will be emitted for sub-directories
            traversed recursively; ``False`` otherwise.
        :type recursive:
            ``bool``
        :return:
            An :class:`ObservedWatch` object instance representing
            a watch.
        """
        with self._lock:
            watch = ObservedWatch(path, recursive)
            self._add_handler_for_watch(event_handler, watch)

            # If we don't have an emitter for this watch already, create it.
            if self._emitter_for_watch.get(watch) is None:
                kwargs = {"event_queue": self.event_queue,
                          "watch": watch,
                          "timeout": self.timeout}
                if issubclass(self._emitter_class, DiscriminatedPollingEmitter):
                    kwargs["exclude_paths"] = exclude_paths
                    logger.debug(kwargs)
                emitter = self._emitter_class(**kwargs)
                self._add_emitter(emitter)
                if self.is_alive():
                    emitter.start()
            self._watches.add(watch)
        return watch
