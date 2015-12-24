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

from ronin.events import RoninEventHandler
from ronin.strategies import StrategyFactory
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from pprint import pprint
import json
import logging
import os
import sys
import time

#: Perform basic logging configuration
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

#: Configure root level logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logger.addHandler(StreamHandler(stream=sys.stdout))


class Manifest(object):
    """
    The Manifest is the representation of the instructions to `ronin` for a
    given directory. It lists the path that files within the `ronin`-enabled
    directory should be syncrhonized to, it lists what files and directories
    should be excluded, provides information on whether the synchronization
    operation should be elevated, etc.

    A manifest file (i.e. `ronin.json`) is a JSON file that contains each of
    the manifest options as a root-level key, e.g.::

    {
      "type": "rsync",
      "path": "/usr/share/mydir",
      "elevate": true,
      "args": ["--verbose"],
      "exclude": [
        ".git"
      ]
    }

    :param manifest_path: Optional. The path to the manifest file. If
        provided it will be parsed when the manifest is instantiated.
    """

    def __init__(self, manifest_path=None):
        #: The individual arguments that should be passed into the handler
        #: for file synchronization.
        self.args = None

        #: The destination directory that the contents of the directory
        #: containing the manifest should be synchronized with.
        self.path = None

        #: Whether or not file synchronization operations should be elevated
        #: and performed by a super user or administrator.
        self.elevate = False

        #: The collection of files and/or directories that should be excluded
        #: from synchronization.
        self.exclude = None

        #: The strategy to use for file syncrhonization, e.g. "rsync"
        self.type = None

        if manifest_path:
            self.parse(manifest_path)

    def __repr__(self):
        return "<Manifest(type='{0}', destination='{1}')>".format(self.type, self.dest)

    def apply(self, **kwargs):
        """
        Assign manifest properties from the passed keyword arguments.

        :param kwargs: the keyword arguments that may be used to assign this
            manifest's properties::

            - args
            - elevate
            - exclude
            - path
            - type
        """
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                logger.debug("Setting manifest property: {0}={1}".format(key, value))
                setattr(self, key, value)

    @property
    def destination(self):
        """
        Return the destination that files in the manifest directory should
        be synchronized with.
        """
        # TODO: Support remote (i.e. SSH) destinations
        return self.path

    def parse(self, manifest_path):
        """
        Parse the data from the manifest file.

        :param manifest: the manifest file.
        """
        logger.debug("Parsing manifest located at: {0}".format(manifest_path))
        with open(manifest_path) as data_file:
            data = json.load(data_file)
            self.apply(**data)


class Ronin(object):
    """
    The class representing the `ronin` process. Ronin is responsible for
    triggering the file synchronization operation, `ronin` may be invoked
    either as an independent process or as a continuous operation that
    watches and reacts to changes in the file system.

    The `ronin` process can be launched from the command line

    :param source: The directory containing the manifest file.
    :param loglevel: Optional. The level that messages should be logged at.
        Default: `logging.INFO`.
    :param logfile: Optional. The file that messages should be recorded to.
        Default: `/var/log/ronin/ronin.log`
    :param watch: Optional. Whether the `source` directory should be watched
        for changes. Default: `False`.
    :param poll: Optional. If watching a directory, whether polling should
        be used instead of events. Default: `False`.
    """

    #: The maximum number of bytes that a log file should be. (2MB)
    LOG_FILE_BYTE_SIZE = 2097152

    def __init__(self, source, **kwargs):
        #: The level of detail that messages should be logged at, by default
        #: logging.INFO.
        self.loglevel = logging.INFO

        #: The file that persistent log messages should be recorded to.
        self.logfile = self.default_logfile

        #: If watching a directory for changes, this indicates whether or not
        #: ronin should be polling for this changes or relying on file system
        #: events.
        #:
        #: If ronin is being used to synchronize files through a shared folder
        #: polling must be turned on because file system events are not
        #: guaranteed to trigger if a system outside of the directory changes
        #: the files.
        self.poll = False

        #: The source directory from which files will be copied during
        #: the synchronization.
        self.source = source

        #: The strategy that will be invoked when running Ronin.
        self.strategy = None

        #: Whether or not the source directory should be watched for changes.
        #: If the source directory is not being watched, ronin will run once
        #: and then exit.
        self.watch = False

        for key, value in kwargs.iteritems():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

        if self.source is None:
            raise TypeError("Source must not be None.")

        #: Initialize
        self.init_logging()

        manifest = self.read_manifest()
        factory = StrategyFactory()
        self.strategy = factory.get_strategy(self.source, manifest)

    def __repr__(self):
        return "<Ronin(source='{0}', watch='{1}', poll='{2}')>".format(self.source, self.watch, self.poll)

    @property
    def default_logfile(self):
        """
        Return the default logfile that messages should be written to.
        """
        path = os.path.abspath(".")
        if os.name == "posix" or os.name == "os2":
            path = os.path.abspath("/var/log/ronin/ronin.log")
        return path

    def init_logging(self):
        """
        Initialize logging for the application.
        """
        path = os.path.dirname(self.logfile)
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise
        formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        rfh = RotatingFileHandler(filename=self.logfile,
                                  maxBytes=Ronin.LOG_FILE_BYTE_SIZE,
                                  backupCount=10)
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)
        logger.setLevel(self.loglevel)

    def read_manifest(self):
        """
        Read the manifest located in the `source` directory and, if it exists,
        construct a new Manifest object from it.
        """
        logger.debug("Reading manifest file from source: {0}".format(self.source))
        manifest_path = os.path.join(self.source, "ronin.json")
        if not os.path.exists(manifest_path):
            raise IOError("Source directory: {0} does not contain ronin.json file.".format(self.source))
        manifest = Manifest(manifest_path)
        return manifest

    def run(self):
        """
        Execute the application's logic, invoking the file synchronization
        defined by the strategy. If Ronin is configured to watch the source
        directory for changes, it will react to any changes within the
        file system.
        """
        if self.watch:
            self.run_watch()
        else:
            self.strategy.invoke()
        logger.info("Goodbye!")

    def run_watch(self):
        if self.poll:
            from watchdog.observers.polling import PollingObserver as Observer
        else:
            from watchdog.observers import Observer

        event_handler = RoninEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.source, recursive=True)
        observer.start()

        try:
            logger.info("Watching directory: '{0}' for changes (poll={1})".format(self.source, self.poll))
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping watcher...")
            observer.stop()
        observer.join()
