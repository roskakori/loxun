"""
Tests for loxun.
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
import doctest
import logging
import sys
import unittest
from StringIO import StringIO

import loxun

def _createXmlStringIoWriter(pretty=True, prolog=False):
    out = StringIO()
    result = loxun.XmlWriter(out, pretty=pretty, prolog=prolog)
    return result

def _getXmlText(writer):
    assert writer
    writer.output.seek(0)
    result = [line.rstrip("\r\n") for line in writer.output]
    return result

class XmlWriterTest(unittest.TestCase):
    def _assertXmlTextEqual(self, writer, actual):
        assert writer
        self.assertEqual(_getXmlText(writer), actual)
    
    def testComment(self):
        xml = _createXmlStringIoWriter()
        xml.comment("some comment")
        xml.close()
        self._assertXmlTextEqual(xml, ["<!-- some comment -->"])

        xml = _createXmlStringIoWriter()
        xml.comment(" some comment ")
        xml.close()
        self._assertXmlTextEqual(xml, ["<!-- some comment -->"])

        xml = _createXmlStringIoWriter()
        xml.comment("")
        xml.close()
        self._assertXmlTextEqual(xml, ["<!--  -->"])

        xml = _createXmlStringIoWriter()
        xml.comment("some comment", embedInBlanks=False)
        xml.close()
        self._assertXmlTextEqual(xml, ["<!--some comment-->"])

    def testCommentWithMultipleLines(self):
        xml = _createXmlStringIoWriter()
        xml.comment("some comment\nspawning multiple\nlines")
        xml.close()
        self._assertXmlTextEqual(xml, ["<!--", "some comment", "spawning multiple", "lines", "-->"])

        xml = _createXmlStringIoWriter()
        xml.startTag("tag")
        xml.comment("some comment\nspawning multiple\nlines")
        xml.endTag()
        xml.close()
        self._assertXmlTextEqual(xml, ["<tag>", "  <!--", "  some comment", "  spawning multiple", "  lines", "  -->", "</tag>"])

    def testBrokenComment(self):
        xml = _createXmlStringIoWriter()
        self.assertRaises(loxun.XmlError, xml.comment, "--")
        self.assertRaises(loxun.XmlError, xml.comment, "", embedInBlanks=False)
        xml.close()
        self._assertXmlTextEqual(xml, [])
        
    def testScopedNamespace(self):
        xml = _createXmlStringIoWriter()
        xml.addNamespace("na", "ua")
        xml.startTag("na:ta")
        xml.addNamespace("nb1", "ub1")
        xml.addNamespace("nb2", "ub2")
        xml.startTag("nb1:tb")
        xml.endTag()
        xml.startTag("na:taa")
        xml.tag("na:tab")
        xml.endTag()
        xml.endTag()
        self._assertXmlTextEqual(xml, [
            "<na:ta xlmns:na=\"ua\">",
            "  <nb1:tb xlmns:nb1=\"ub1\" xlmns:nb2=\"ub2\">",
            "  </nb1:tb>",
            "  <na:taa>",
            "    <na:tab />",
            "  </na:taa>",
            "</na:ta>"
        ])

def createTestSuite():
    """
    TestSuite including all unit tests and doctests found in the source code.
    """
    result = unittest.TestSuite()
    loader = unittest.TestLoader()

    # TODO: Automatically discover doctest cases.
    result.addTest(doctest.DocTestSuite(loxun))

    # TODO: Automatically discover test cases.
    allTests = [
        XmlWriterTest
    ]
    for testCaseClass in allTests:
        result.addTest(loader.loadTestsFromTestCase(testCaseClass))

    return result

def main():
    """
    Run all tests.
    """
    result = 0
    testCount = 0
    errorCount = 0
    failureCount = 0

    allTestSuite = createTestSuite()
    testResults = unittest.TextTestRunner(verbosity=2).run(allTestSuite)
    testCount += testResults.testsRun
    failureCount += len(testResults.failures)
    errorCount += len(testResults.errors)
    print "test_all: ran %d tests with %d failures and %d errors" % (testCount, failureCount, errorCount)
    if (errorCount + failureCount) > 0:
        result = 1
    return result

if __name__ == "__main__": # pragma: no cover
    logging.basicConfig()
    logging.getLogger("test_loxun").setLevel(logging.WARNING)
    sys.exit(main())
