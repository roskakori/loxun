"""
Installer for loxun.

Developer cheat sheet
---------------------

Create the installer archive::

  $ python setup.py sdist --formats=zip

Upload release to PyPI::

  $ python test/test_loxun.py
  $ python setup.py sdist --formats=zip upload

Tag a release::

  $ git tag -a -m "Tagged version 1.x." v1.x
  $ git push --tags

Build API documentation
-----------------------

Patch Epydoc 3.0.1 to work with docutils 0.6:

In ``epydoc/markup/restructuredtext.py``, change in 
``_SummaryExtractor.__init__()``::

  # Extract the first sentence.
  for child in node:
     if isinstance(child, docutils.nodes.Text):
         # FIXED: m = self._SUMMARY_RE.match(child.data)
         text = child.astext()
         m = self._SUMMARY_RE.match(text)
         if m:
             summary_pieces.append(docutils.nodes.Text(m.group(1)))
             # FIXED: other = child.data[m.end():]
             other = text[m.end():]
             if other and not other.isspace():
                 self.other_docs = True
             break
     summary_pieces.append(child)

Run::

  $ python setup.py api
"""
# Copyright (C) 2010-2011 Thomas Aglassinger
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Required patch for Epydoc 3.0.1 to work with docutils 0.6:
# In epydoc/markup/restructuredtext.py, change in _SummaryExtractor.__init__():
# Extract the first sentence.
#  for child in node:
#     if isinstance(child, docutils.nodes.Text):
#         # FIXED: m = self._SUMMARY_RE.match(child.data)
#         text = child.astext()
#         m = self._SUMMARY_RE.match(text)
#         if m:
#             summary_pieces.append(docutils.nodes.Text(m.group(1)))
#             # FIXED: other = child.data[m.end():]
#             other = text[m.end():]
#             if other and not other.isspace():
#                 self.other_docs = True
#             break
#     summary_pieces.append(child)
import errno
import os.path
import subprocess
from distutils.core import setup
from distutils.cmd import Command

import loxun

def _makeFolders(path):
    try:
        os.makedirs(path)
    except OSError, error:
        if error.errno != errno.EEXIST:
            raise

class _ApiCommand(Command):
    """
    Command for setuptools to build API documentation.
    """
    description = "build API documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        _makeFolders(os.path.join("build", "site", "api"))
        epydocCall = ["epydoc", "--config", "epydoc.config"]
        print " ".join(epydocCall)
        subprocess.check_call(epydocCall)

setup(
    name="loxun",
    version=loxun.__version__,
    py_modules=["loxun"],
    description="large output in XML using unicode and namespaces",
    keywords="xml output stream large big huge namespace unicode memory footprint",
    author="Thomas Aglassinger",
    author_email="roskakori@users.sourceforge.net",
    url="http://pypi.python.org/pypi/loxun/",
    license="GNU Lesser General Public License 3 or later",
    long_description=loxun.__doc__, #@UndefinedVariable
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        # TODO: Test with Python 2.4. Who knows, it might actually work.
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    cmdclass={"api": _ApiCommand}
)
