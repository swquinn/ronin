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

from ronin import Ronin
import argparse
import logging
import os

#: Logging
logger = logging.getLogger(__name__)


class CommandLine():
    """
    The command line interpreter for the `ronin` process.


    """

    #: The logging apparatus
    logger = None

    #: The argument parser.
    parser = None

    # usage: vagrant [options] <command> [<args>]

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Synchronize directory contents.')
        self.parser.add_argument("-l", "--logfile", metavar="FILENAME", type=str, help="Use FILENAME as logfile path", required=False)
        self.parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.", required=False)
        self.parser.add_argument("--watch", action="store_true", help="Watch target for changes.", required=False)
        self.parser.add_argument("--poll", action="store_true", help="Use polling to detect file system changes instead of events.", required=False)
        self.parser.add_argument("--timeout", metavar="NUM", type=float, help="Timeout in seconds to attempt to syncrhonize before giving up.", required=False)

        self.parser.add_argument("target", help="The directory containing the ronin manifest file (ronin.json).")

    def parse(self):
        """
        Parse the command line arguments and return an instance of the
        `ronin` process.
        """
        args = self.parser.parse_args()

        #: Resolve the path to the source directory (or, rather our target)
        path = args.target
        if os.path.isfile:
            os.path.dirname(args.target)
        path = os.path.abspath(os.path.expanduser(path) + os.sep)

        #: Create the Ronin instance.
        ronin = Ronin(path,
                      logfile=args.logfile,
                      loglevel=logging.DEBUG if args.verbose else logging.INFO,
                      watch=args.watch,
                      poll=args.poll)
        return ronin
