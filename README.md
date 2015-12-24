ronin
=====

Ronin is a complementary tool to Vagrant (or any VM, really). It is a file
synchronization utility that acts as a wrapper around `rsync`, but may also
wrap other file synchronization strategies.

The idea is to install Ronin on a VM or workstation that needs to synchronize
files from a directory used for development to a directory that is used for
testing, or running code. Ronin was explicitly developed to solve this need
within VMs where attempting to serve web content from a mounted/shared
directory (e.g. the development directory) created impossibly long response
times.

While NFS and `rsync` may work for some people, Ronin was designed with the
idea that working within a shared directory between host and VM should result
in seamless file synchronization, and support for `rsync` or NFS on Windows
environments is dubious at best, at worst it isn't there at all. So instead,
Ronin would operate as a platform agnostic tool to watch directories for
changes and initiate the synchronization of files.

For the time being, Ronin works best if installed on the guest and is
instructed to watch (by polling) the shared directory, since file system
change events are not fired within a guest VM when files are changed from
outside of the guest.
