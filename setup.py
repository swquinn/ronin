##############################################################################
#
# Copyright (c) 2006-2015 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
import sys

py_version = sys.version_info[:2]

if py_version < (2, 6):
    raise RuntimeError("On Python 2, Ronin requires Python 2.6 or later")
elif (3, 0) < py_version < (3, 2):
    raise RuntimeError("On Python 3, Ronin requires Python 3.2 or later")

requires = ["watchdog >= 0.8.3"]
tests_require = []
if py_version < (3, 3):
    tests_require.append("mock")

testing_extras = tests_require + [
    "nose",
    "nose-cov",
    ]

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, "README.md")).read()
    CHANGES = open(os.path.join(here, "CHANGELOG")).read()
except:
    README = """\
Ronin is a tool that allows users to synchronize files using
various backends between directories. """
    CHANGES = ""

CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: No Input/Output (Daemon)",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: MacOS",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: System :: Monitoring",
    "Topic :: System :: Utilities",
]

version_txt = os.path.join(here, "ronin/version.txt")
supervisor_version = open(version_txt).read().strip()

dist = setup(
    name="ronin",
    version=ronin_version,
    license="MIT License (http://opensource.org/licenses/MIT)",
    url="https://github.com/swquinn/ronin/",
    description="A tool for handling file synchronization",
    long_description=README + "\n\n" + CHANGES,
    classifiers=CLASSIFIERS,
    author="Sean W. Quinn",
    author_email="sean.quinn@extesla.com",
    maintainer="Sean W. Quinn",
    maintainer_email="sean.quinn@extesla.com",
    packages=find_packages(),
    install_requires=requires,
    extras_require={
        "testing": testing_extras,
        },
    tests_require=tests_require,
    include_package_data=True,
    zip_safe=False,
    test_suite="test",
    entry_points={
        "console_scripts": [
            "ronin = ronin:main",
            "ronind = ronin.ronind:main",
        ],
    },
)
