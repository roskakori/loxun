"""
Installer for loxun.

To create the installer archive, run::

  python setup.py sdist --formats=zip
"""
# Copyright (C) 2010 Thomas Aglassinger
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from distutils.core import setup

import loxun

setup(
    name="loxun",
    version=loxun.VERSION,
    py_modules=["loxun"],
    description="large output in XML using unicode and namespaces",
    keywords="xml output stream large big huge namespace unicode memory footprint",
    author="Thomas Aglassinger",
    author_email="roskakori@users.sourceforge.net",
    url="http://pypi.python.org/pypi/loxun/",
    license="GNU Lesser General Public License 3 or later",
    long_description=loxun.__doc__, #@UndefinedVariable
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        # TODO: Test with Python 2.4. Who knows, it might actually work.
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Markup :: XML",
    ],
)
