# -*- coding: iso-8859-15 -*-
"""
Tests for loxun.
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

# Allow "with" statement to be used in tests even for Python 2.5
from __future__ import with_statement

import doctest
import logging
import random
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

_randy = random.Random()

def _randomName():
    result = u""
    for _ in range(5 + _randy.randint(0, 10)):
        result += unichr(_randy.randint(ord("a"), ord("z")))
    return result

class XmlWriterTest(unittest.TestCase):
    def _assertXmlTextEqual(self, writer, actual):
        assert writer
        self.assertEqual(_getXmlText(writer), actual)
    
    def testCanSetEncoding(self):
        xml = loxun.XmlWriter(StringIO(), encoding='iso-8859-15')
        self.assertEqual(xml.encoding, u'iso-8859-15')

    def testUnicodeEuro(self):
        xml = _createXmlStringIoWriter()
        xml.text(u"\u20ac")
        self._assertXmlTextEqual(xml, ["\xe2\x82\xac"])

    def testInitIndent(self):
        out = StringIO()
        xml = loxun.XmlWriter(out, indent="\t")
        self.assertEquals(xml._indent, u"\t")
        xml = loxun.XmlWriter(out, indent="    ")
        self.assertEquals(xml._indent, u"    ")
        try:
            loxun.XmlWriter(out, indent="xxx")
        except AssertionError, error:
            self.assertEquals(str(error), "`indent` must contain only blanks or tabs but also has: u'xxx'")

    def testInitNewline(self):
        out = StringIO()
        for newline in ["\r", "\n", "\r\n"]:
            xml = loxun.XmlWriter(out, newline=newline)
            self.assertEquals(xml._newline, unicode(newline, "ascii"))
        try:
            loxun.XmlWriter(out, newline="xxx")
        except AssertionError, error:
            self.assertEquals(str(error), "`newline` is u'xxx' but must be one of: [u'\\r', u'\\n', u'\\r\\n']")

    def testIndentWithPretty(self):
        out = StringIO()
        xml = loxun.XmlWriter(out, indent="\t")
        xml.startTag("a")
        xml.startTag("b")
        xml.tag("c")
        xml.text("some text")
        xml.endTag("b")
        xml.endTag("a")
        self._assertXmlTextEqual(xml, ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<a>", "\t<b>", "\t\t<c />", "\t\tsome text", "\t</b>", "</a>"])

    def testDefautltIndentWithoutPretty(self):
        # Regression test for issue #1.
        out = StringIO()
        xml = loxun.XmlWriter(out, pretty=False)
        xml.startTag("a")
        xml.startTag("b")
        xml.tag("c")
        xml.text("some text")
        xml.endTag("b")
        xml.endTag("a")
        self._assertXmlTextEqual(xml, ["<?xml version=\"1.0\" encoding=\"utf-8\"?><a><b><c/>some text</b></a>"])

    def testIsoEuro(self):
        out = StringIO()
        xml = loxun.XmlWriter(out, sourceEncoding="iso-8859-15", prolog=False)
        xml.text("\xa4")
        self._assertXmlTextEqual(xml, ["\xe2\x82\xac"])
        
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

    def testNamespacedTag(self):
        xml = _createXmlStringIoWriter()
        xml.addNamespace("x", "http://xxx/");
        xml.tag("x:a")
        xml.close()
        self._assertXmlTextEqual(xml, ["<x:a xmlns:x=\"http://xxx/\" />"])

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
            "<na:ta xmlns:na=\"ua\">",
            "  <nb1:tb xmlns:nb1=\"ub1\" xmlns:nb2=\"ub2\" />",
            "  <na:taa>",
            "    <na:tab />",
            "  </na:taa>",
            "</na:ta>"
        ])

    def testBrokenScopedNamespacedTag(self):
        xml = _createXmlStringIoWriter()
        xml.startTag("outer")
        xml.addNamespace("x", "http://xxx/");
        xml.tag("x:inner")
        self.assertRaises(loxun.XmlError, xml.startTag, "x:outer")

    def testWithOk(self):
        out = StringIO()       
        with loxun.XmlWriter(out) as xml:
            xml.tag("x")

    def testWithMissingEndTag(self):
        out = StringIO()       
        try:
            with loxun.XmlWriter(out) as xml:
                xml.startTag("x")
            self.fail("XmlWriter.__exit__() must detect missing </x>")
        except loxun.XmlError:
            # Ignore expected error.
            pass

    def testWithException(self):
        out = StringIO()       
        try:
            with loxun.XmlWriter(out) as xml:
                xml.startTag("x")
                raise ValueError("test")
        except ValueError, error:
            # Ignore expected error.
            self.assertEquals(unicode(error), u"test")

    def testPerformance(self):
        out = StringIO()       
        with loxun.XmlWriter(out) as xml:
            tagName = _randomName()
            attributes = {}
            for _ in range(_randy.randint(2, 8)):
                attributes[_randomName()] = ""
            xml.tag(tagName, attributes)

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
