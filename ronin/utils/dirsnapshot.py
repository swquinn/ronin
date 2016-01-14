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
:module: ronin.utils.dirsnapshot
:synopsis: Discriminated directory snapshots and comparison.

.. ADMONITION:: Why "discriminated" directory snapshots?

        When a directory snapshot is taken, it will walk the entire
        directory if the snapshot is recursive. In cases where there
        are a large number of files in one or more directories, the
        act of taking a snapshot can be quite slow. By ignoring the
        discriminated paths, we can potentially increase the speed
        of watchdog if we don't care about the directories with large
        numbers of files.

Classes
-------
.. autoclass:: DiscriminatedDirectorySnapshot
   :members:
   :show-inheritance:

"""

import errno
import os
from stat import S_ISDIR
from watchdog.utils import platform
from watchdog.utils import stat as default_stat
from watchdog.utils.dirsnapshot import DirectorySnapshotDiff


class DiscriminatedDirectorySnapshot(object):
    """
    A snapshot of stat information of files in a directory, that discriminates
    against the ignored paths.

    The directory snapshot will not index any files or directories included in
    the ignored paths. Also, for directories that are excluded, this also
    means that subdirectories beneath and excluded directory will also be
    excluded.

    Otherwise, this works exactly like the ``DirectorySnapshot`` from within
    the ``watchdog.utils.dirsnapshot`` module.

    :param path:
        The directory path for which a snapshot should be taken.
    :type path:
        ``str``
    :param ignore_paths:
        The collection of paths to be excluded from being included in
        directory snapshots.
    :type ignore_paths:
        ``list``
    :param recursive:
        ``True`` if the entire directory tree should be included in the
        snapshot; ``False`` otherwise.
    :type recursive:
        ``bool``
    :param walker_callback:
        .. deprecated:: 0.7.2
    :param stat:
        Use custom stat function that returns a stat structure for path.
        Currently only st_dev, st_ino, st_mode and st_mtime are needed.

        A function with the signature ``walker_callback(path, stat_info)``
        which will be called for every entry in the directory tree.
    :param listdir:
        Use custom listdir function. See ``os.listdir`` for details.
    """

    def __init__(self, path, recursive=True, ignore_paths=None,
                 walker_callback=(lambda p, s: None),
                 stat=default_stat,
                 listdir=os.listdir):
        self._ignore_paths = ignore_paths
        self._stat_info = {}
        self._inode_to_path = {}

        st = stat(path)
        self._stat_info[path] = st
        self._inode_to_path[(st.st_ino, st.st_dev)] = path

        def walk(root):
            try:
                paths = [os.path.join(root, name) for name in listdir(root)]
            except OSError as e:
                # Directory may have been deleted between finding it in the directory
                # list of its parent and trying to delete its contents. If this
                # happens we treat it as empty.
                if e.errno == errno.ENOENT:
                    return
                else:
                    raise
            entries = []
            for p in paths:
                try:
                    if self.is_proccess_path(p):
                        entries.append((p, stat(p)))
                except OSError:
                    continue
            for _ in entries:
                yield _
            if recursive:
                for path, st in entries:
                    if S_ISDIR(st.st_mode):
                        for _ in walk(path):
                            yield _

        for p, st in walk(path):
            i = (st.st_ino, st.st_dev)
            self._inode_to_path[i] = p
            self._stat_info[p] = st
            walker_callback(p, st)

    def is_proccess_path(self, path):
        """
        """
        if self._ignore_paths is not None and path in self._ignore_paths:
            return False
        return True

    @property
    def paths(self):
        """
        Set of file/directory paths in the snapshot.
        """
        return set(self._stat_info.keys())

    def path(self, id):
        """
        Returns path for id. None if id is unknown to this snapshot.
        """
        return self._inode_to_path.get(id)

    def inode(self, path):
        """ Returns an id for path. """
        st = self._stat_info[path]
        return (st.st_ino, st.st_dev)

    def isdir(self, path):
        return S_ISDIR(self._stat_info[path].st_mode)

    def mtime(self, path):
        return self._stat_info[path].st_mtime

    def stat_info(self, path):
        """
        Returns a stat information object for the specified path from
        the snapshot.

        Attached information is subject to change. Do not use unless
        you specify `stat` in constructor. Use :func:`inode`, :func:`mtime`,
        :func:`isdir` instead.

        :param path:
            The path for which stat information should be obtained
            from a snapshot.
        """
        return self._stat_info[path]

    def __sub__(self, previous_dirsnap):
        """Allow subtracting a DirectorySnapshot object instance from
        another.

        :returns:
            A :class:`DirectorySnapshotDiff` object.
        """
        return DirectorySnapshotDiff(previous_dirsnap, self)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self._stat_info)
