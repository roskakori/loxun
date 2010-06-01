"""
loxun is a Python module to write large output in XML using Unicode and
namespaces. Of course you can also use it for small XML output with plain 8
bit strings and no namespaces.

loxun's features are:

* **small memory foot print**: the document is created on the fly by writing to
  an output stream, no need to keep all of it in memory.

* **easy to use namespaces**: simply add a namespace and refer to it using the
  standard ``namespace:tag`` syntax.

* **mix unicode and string**: pass both unicode or plain 8 bit strings to any
  of the methods. Internally loxun converts them to unicode, so once a
  parameter got accepted by the API you can rely on it not causing any
  messy ``UnicodeError`` trouble.

* **automatic escaping**: no need to manually handle special characters such
  as ``<`` or ``&`` when writing text and attribute values.

* **robustness**: while you write the document, sanity checks are performed on
  everything you do. Many silly mistakes immediately result in an
  ``XmlError``, for example missing end elements or references to undeclared
  namespaces.

* **open source**: distributed under the GNU Lesser General Public License 3
  or later.

Here is a very basic example. First you have to create an output stream. In
many cases this would be a file, but for the sake of simplicity we use a
``StringIO`` here:

    >>> from StringIO import StringIO
    >>> out = StringIO()

Then you can create an `XmlWriter` to write to this output:

    >>> xml = XmlWriter(out)

Now write the content:

    >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml")
    >>> xml.startTag("xhtml:html")
    >>> xml.startTag("xhtml:body")
    >>> xml.text("Hello world!")
    >>> xml.tag("xhtml:img", {"src": "smile.png", "alt": ":-)"})
    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()

And the result is:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <xhtml:html xmlns:xhtml="http://www.w3.org/1999/xhtml">
      <xhtml:body>
        Hello world!
        <xhtml:img alt=":-)" src="smile.png" />
      </xhtml:body>
    </xhtml:html>

Writing a simple document
=========================

The following example creates a very simple XHTML document.

To make it simple, the output goes to a string, but you could also use
a file that has been created using
``codecs.open(filename, "wb", encoding)``.

    >>> from StringIO import StringIO
    >>> out = StringIO()

First create an `XmlWriter` to write the XML code to the specified output:

    >>> xml = XmlWriter(out)

This automatically adds the XML prolog:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>

Next add the ``<html>`` start tag:

    >>> xml.startTag("html")

Now comes the <body>. To pass attributes, specify them in a dictionary.
So in order to add::

    <body id="top">

use:

    >>> xml.startTag("body", {"id": "top"})

Let' add a little text so there is something to look at:

    >>> xml.text("Hello world!")

Wrap it up: close all elements and the document.

    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()

And this is what we get:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <html>
      <body id="top">
        Hello world!
      </body>
    </html>

Using namespaces
================

Now the same thing but with a namespace. First create the prolog
and header like above:

    >>> out = StringIO()
    >>> xml = XmlWriter(out)

Next add the namespace:

    >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml")

Now elements can use qualified tag names using a colon (:) to separate
namespace and tag name:

    >>> xml.startTag("xhtml:html")
    >>> xml.startTag("xhtml:body")
    >>> xml.text("Hello world!")
    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()

As a result, tag names are now prefixed with "xhtml:":

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <xhtml:html xmlns:xhtml="http://www.w3.org/1999/xhtml">
      <xhtml:body>
        Hello world!
      </xhtml:body>
    </xhtml:html>

Working with non ASCII characters
=================================

Sometimes you want to use characters outside the ASCII range, for example
German Umlauts, the Euro symbol or Japanese Kanji. The easiest and performance
wise best way is to use Unicode strings. For example:

    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> xml = XmlWriter(out, prolog=False)
    >>> xml.text(u"The price is \\u20ac 100") # Unicode of Euro symbol
    >>> out.getvalue().rstrip("\\r\\n")
    'The price is \\xe2\\x82\\xac 100'

Notice the "u" before the string passed to `XmlWriter.text()`, it declares the
string to be a unicode string that can hold any character, even those that are
beyond the 8 bit range.

Also notice that in the output the Euro symbol looks very different from the
input. This is because the output encoding is UTF-8 (the default), which
has the advantage of keeping all ASCII characters the same and turning any
characters with a code of 128 or more into a sequence of 8 bit bytes that
can easily fit into an output stream to a binary file or ``StringIO``.

If you have to stick to classic 8 bit string parameters, loxun attempts to
convert them to unicode. By default it assumes ASCII encoding, which does
not work out as soon as you use a character outside the ASCII range:

    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> xml = XmlWriter(out, prolog=False)
    >>> xml.text("The price is \\xa4 100") # ISO-8859-15 code of Euro symbol
    Traceback (most recent call last):
        ...
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xa4 in position 13: ordinal not in range(128)

In this case you have to tell the writer the encoding you use by specifying
the the ``sourceEncoding``:

    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> xml = XmlWriter(out, prolog=False, sourceEncoding="iso-8859-15")

Now everything works out again:

    >>> xml.text("The price is \\xa4 100") # ISO-8859-15 code of Euro symbol
    >>> out.getvalue().rstrip("\\r\\n")
    'The price is \\xe2\\x82\\xac 100'

Of course in practice you will not mess around with hex codes to pass your
texts. Instead you just specify the source encoding using the mechanisms
described in PEP 263,
`Defining Python Source Code Encodings <http://www.python.org/dev/peps/pep-0263/>`_:

Changing the XML prolog
=======================

When you create a writer, it automatically write an XML prolog
processing instruction to the output. This is what the default prolog
looks like:

    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> xml = XmlWriter(out)
    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>

You can change the version or encoding:

    >>> out = StringIO()
    >>> xml = XmlWriter(out, encoding=u"ascii", version=u"1.1")
    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.1" encoding="ascii"?>

To completely omit the prolog, set the parameter ``prolog=False``:

    >>> out = StringIO()
    >>> xml = XmlWriter(out, prolog=False)
    >>> out.getvalue()
    ''

Version history
===============


Version 0.6, xx-May-2010
------------------------

* Cleaned up documentation.

Version 0.5, 25-May-2010
------------------------

* Fixed typo in namespace attribute name.
* Fixed adding of namespaces before calls to `XmlWriter.tag()` which resulted
  in an `XmlError`.

Version 0.4, 21-May-2010
------------------------

* Added option ``sourceEncoding`` to simplify processing of classic strings.
  The manual section "Working with non ASCII characters" explains how to use
  it.

Version 0.3, 17-May-2010
------------------------

* Added scoped namespaces which are removed automatically by
  `XmlWriter.endTag()`.
* Changed ``text()`` to normalize newlines and white space if pretty printing
  is enabled.
* Moved writing of XML prolog to the constructor and removed
  ``XmlWriter.prolog()``. To omit the prolog, specify ``prolog=False`` when
  creating the `XmlWriter`. If you later want to write the prolog yourself,
  use `XmlWriter.processingInstruction()`.
* Renamed ``*Element()`` to ``*Tag`` because they really only write tags, not
  whole elements.

Version 0.2, 16-May-2010
------------------------

* Added `XmlWriter.comment()`, `XmlWriter.cdata()` and
  `XmlWriter.processingInstruction()` to write these specific XML constructs.
* Added indentation and automatic newline to text if pretty printing is
  enabled.
* Removed newline from prolog in case pretty printing is disabled.
* Fixed missing "?" in prolog.

Version 0.1, 15-May-2010
------------------------

* Initial release.
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

# Developer cheat sheet
#
# Build release:
# > python setup.py sdist --formats=zip
#
# Upload release to PyPI:
# > python setup.py sdist --formats=zip upload
#
# Tag a release in the repository:
# > svn copy -m "Added tag for version 0.x." file:///Users/${USER}/Repositories/huxml/trunk file:///Users/${USER}/Repositories/huxml/tags/0.x
import collections
import os
import xml.sax.saxutils
from StringIO import StringIO

__version__ = "0.6"
VERSION_REV, VERSION_DATE = "$Id$".split()[2:4]

class XmlError(Exception):
    """
    Error raised when XML can not be generated.
    """
    pass

def _quoted(value):
    _assertIsUnicode(u"value", value)
    return xml.sax.saxutils.quoteattr(value)

def _validateNotEmpty(name, value):
    """
    Validate that ``value`` is not empty and raise `XmlError` in case it is.
    """
    assert name
    if not value:
        raise XmlError(u"%s must not be empty" % name)

def _validateNotNone(name, value):
    """
    Validate that ``value`` is not ``None`` and raise `XmlError` in case it is.
    """
    assert name
    if value is None:
        raise XmlError(u"%s must not be %r" % (name, None))

def _validateNotNoneOrEmpty(name, value):
    """
    Validate that ``value`` is not empty or ``None`` and raise `XmlError` in case it is.
    """
    _validateNotNone(name, value)
    _validateNotEmpty(name, value)

def _assertIsUnicode(name, value):
    assert (value is None) or isinstance(value, unicode), \
        u"value for %r must be of type unicode but is: %r" % (name, value)

def _splitPossiblyQualifiedName(name, value):
    """
    A pair ``(namespace, name)`` derived from ``name``.

    A fully qualified name:

        >>> _splitPossiblyQualifiedName(u"tag name", u"xhtml:img")
        (u'xhtml', u'img')

    A name in the default namespace:

        >>> _splitPossiblyQualifiedName(u"tag name", u"img")
        (None, u'img')

    Improper names result in an `XmlError`:

        >>> _splitPossiblyQualifiedName(u"x", u"")
        Traceback (most recent call last):
        ...
        XmlError: x must not be empty
    """
    assert name
    _assertIsUnicode(u"name", name)
    _assertIsUnicode(u"value", value)

    colonIndex = value.find(u":")
    if colonIndex == -1:
        _validateNotEmpty(name, value)
        result = (None, value)
    else:
        namespacePart = value[:colonIndex]
        _validateNotEmpty(u"namespace part of %s", namespacePart)
        namePart = value[colonIndex+1:]
        _validateNotEmpty(u"name part of %s", namePart)
        result = (namespacePart, namePart)
    # TODO: validate that all parts are NCNAMEs.
    return result

def _joinPossiblyQualifiedName(namespace, name):
    _assertIsUnicode(u"namespace", namespace)
    assert name
    _assertIsUnicode(u"name", name)
    if namespace:
        result = u"%s:%s" % (namespace, name)
    else:
        result = name
    return result

class XmlWriter(object):
    """
    Writer for large output in XML optionally supporting Unicode and
    namespaces.
    """
    # Marks to start/end CDATA.
    _CDATA_START = u"<![CDATA["
    _CDATA_END = u"]]>"

    # Marks to start/end processing instrution.
    _PROCESSING_START = u"<?"
    _PROCESSING_END = u"?>"

    # Possible value for _writeTag()'s ``close`` parameter.
    _CLOSE_NONE = u"none"
    _CLOSE_AT_START = u"start"
    _CLOSE_AT_END = u"end"

    def __init__(self, output, pretty=True, encoding=u"utf-8", errors=u"strict", prolog=True, version=u"1.0", sourceEncoding="ascii"):
        """
        Initialize ``XmlWriter`` writing to ``output``.

        The ``output`` can be anything that has a ``write(data)`` method,
        typically a filelike object. The writer accesses the ``output`` as
        stream, so it does not have to support any methods for random
        access like ``seek()``.

        In case you write to a file, use ``"wb"`` as ``mode`` for ``open()``
        to prevent messed up newlines.

        Set ``pretty`` to ``False`` if you do not want to the writer to pretty
        print. Keep in mind though that this results in the whole output being
        a single line unless you use `newline()` or write text with newline
        characters in it.

        Set ``encoding`` to the name of the preferred output encoding.

        Set ``errors`` to one of the value possible value for
        ``unicode(..., error=...)`` if you do not want the output to fail with
        a `UnicodeError` in case a character cannot be encoded.

        Set ``prolog`` to ``False`` if you do not want the writer to emit an
        XML prolog processing instruction (like
        ``<?xml version="1.0" encoding="utf-8"?>``).

        Set ``version`` to the value the version attribute in the XML prolog
        should have.

        Set ``sourceEncoding`` to the name of the encoding that plain 8 bit
        strings passed as parameters use.
        """
        assert output is not None
        assert encoding
        assert errors
        assert sourceEncoding
        _validateNotNoneOrEmpty("version", version)
        self._output = output
        self._pretty = pretty
        # TODO: Add indent parameter and property.
        # TODO: Add newline parameter.
        self._indent = u"  "
        self._newline = unicode(os.linesep, "ascii")
        self._encoding = self._unicoded(encoding)
        self._errors = self._unicoded(errors)
        self._namespaces = {}
        self._elementStack = collections.deque()
        self._namespacesToAdd = collections.deque()
        self._isOpen = True
        self._contentHasBeenWritten = False
        self._sourceEncoding = sourceEncoding
        if prolog:
            self.processingInstruction(u"xml", "version=%s encoding=%s" % ( \
                _quoted(self._unicoded(version)),
                _quoted(self._encoding))
            )

    @property
    def isPretty(self):
        """Pretty print writes to the ``output``?"""
        return self._pretty

    @property
    def encoding(self):
        """The encoding used when writing to the ``output``."""
        return self._encoding

    @property
    def output(self):
        """The stream where the output goes."""
        return self._output

    def _scope(self):
        return len(self._elementStack)

    def _encoded(self, text):
        assert text is not None
        _assertIsUnicode(u"text", text)
        return text.encode(self._encoding, self._errors)

    def _unicoded(self, text):
        """
        Same value as ``text`` but converted to unicode in case ``text`` is a
        string. ``None`` remains ``None``.
        """
        if text is None:
            result = None
        elif isinstance(text, unicode):
            result = text
        else:
            result = unicode(text, self._sourceEncoding)
        return result

    def _elementName(self, name, namespace):
        assert name
        if namespace:
            result = u"%s:%s" % (namespace, name)
        else:
            result = name
        return result

    def _validateIsOpen(self):
        if not self._isOpen:
            raise XmlError(u"operation must be performed before writer is closed")

    def _validateNamespaceItem(self, itemName, namespace, qualifiedName):
        if namespace:
            namespaceFound = False
            scopeIndex = self._scope()
            while not namespaceFound and (scopeIndex >= 0):
                namespacesForScope = self._namespaces.get(scopeIndex)
                if namespacesForScope:
                    if namespace in [namespaceToCompareWith for namespaceToCompareWith, _ in namespacesForScope]:
                        namespaceFound = True
                scopeIndex -= 1
            if not namespaceFound:
                raise XmlError(u"namespace '%s' for %s '%s' must be added before use" % (namespace, itemName, qualifiedName))

    def _write(self, text):
        assert text is not None
        _assertIsUnicode(u"text", text)
        self._output.write(self._encoded(text))
        if not self._contentHasBeenWritten and text:
            self._contentHasBeenWritten = True

    def _writeIndent(self):
        self._write(self._indent * len(self._elementStack))

    def _writePrettyIndent(self):
        if self._pretty:
            self._writeIndent()

    def _writePrettyNewline(self):
        if self._pretty:
            self.newline()

    def _writeEscaped(self, text):
        assert text is not None
        _assertIsUnicode("text", text)
        self._write(xml.sax.saxutils.escape(text))

    def newline(self):
        self._write(self._newline)

    def addNamespace(self, name, uri):
        """
        Add namespace to the following elements by adding a ``xmlns``
        attribute to the next tag that is written using `startTag()` or `tag()`.
        """
        # TODO: Validate that name is NCName.
        _validateNotNoneOrEmpty("name", name)
        _validateNotNoneOrEmpty("uri", uri)
        uniName = self._unicoded(name)
        uniUri = self._unicoded(uri)
        namespacesForScope = self._namespaces.get(self._scope())
        namespaceExists = (uniName in self._namespacesToAdd) or (
            (namespacesForScope != None) and (uniName in namespacesForScope)
        )
        if namespaceExists:
            raise ValueError(u"namespace %r must added only once for current scope but already is %r" % (uniName, uniUri))
        self._namespacesToAdd.append((uniName, uniUri))

    def _writeTag(self, namespace, name, close, attributes={}):
        _assertIsUnicode("namespace", namespace)
        assert name
        _assertIsUnicode("name", name)
        assert close
        assert close in (XmlWriter._CLOSE_NONE, XmlWriter._CLOSE_AT_START, XmlWriter._CLOSE_AT_END)
        assert attributes is not None

        actualAttributes = {}

        # TODO: Validate that no "xmlns" attributes are specified by hand.

        # Process new namespaces to add.
        if close in [XmlWriter._CLOSE_NONE, XmlWriter._CLOSE_AT_END]:
            while self._namespacesToAdd:
                namespaceName, uri = self._namespacesToAdd.pop()
                if namespaceName:
                    actualAttributes[u"xmlns:%s" % namespaceName] = uri
                else:
                    actualAttributes[u"xmlns"] = uri
                namespacesForScope = self._namespaces.get(self._scope())
                if namespacesForScope == None:
                    namespacesForScope = []
                    self._namespaces[self._scope()] = namespacesForScope
                assert namespaceName not in [existingName for existingName, _ in namespacesForScope]
                namespacesForScope.append((namespaceName, uri))
                self._namespaces[namespaceName] = uri
        else:
            if self._namespacesToAdd:
                namespaceNames = ", ".join([name for name, _ in self._namespacesToAdd])
                raise XmlError(u"namespaces must be added before startTag() or tag(): %s" % namespaceNames)

        # Convert attributes to unicode.
        for qualifiedAttributeName, attributeValue in attributes.items():
            uniQualifiedAttributeName = self._unicoded(qualifiedAttributeName)
            attributeNamespace, attributeName = _splitPossiblyQualifiedName(u"attribute name", uniQualifiedAttributeName)
            self._validateNamespaceItem(u"attribute", attributeNamespace, attributeName)
            actualAttributes[uniQualifiedAttributeName] = self._unicoded(attributeValue)

        self._validateNamespaceItem(u"tag", namespace, name)
        if namespace:
            element = u"%s:%s" % (namespace, name)
        else:
            element = name
        if self._pretty:
            self._write(self._indent * len(self._elementStack))
        self._write(u"<")
        if close == XmlWriter._CLOSE_AT_START:
            self._write(u"/")
        self._write(element)
        for attributeName in sorted(actualAttributes.keys()):
            _assertIsUnicode(u"attribute name", attributeName)
            value = actualAttributes[attributeName]
            _assertIsUnicode(u"value of attribute %r" % attributeName, value)
            self._write(u" %s=%s" % (attributeName, _quoted(value)))
        if close == XmlWriter._CLOSE_AT_END:
            if self.isPretty:
                self._write(u" ")
            self._write(u"/")
        self._write(u">")
        if self._pretty:
            self.newline()

    def startTag(self, qualifiedName, attributes={}):
        """
        Start tag with name ``qualifiedName``, optionally using a namespace
        prefix separated with a colon (:) and ``attributes``.

        Example names are "img" and "xhtml:img" (assuming the namespace prefix
        "xtml" has been added before using `addNamespace()`).

        Attributes are a dictionary containing the attribute name and value, for
        example::

            {"src": "../some.png", "xhtml:alt": "some image"}
        """
        uniQualifiedName = self._unicoded(qualifiedName)
        namespace, name = _splitPossiblyQualifiedName(u"tag name", uniQualifiedName)
        self._writeTag(namespace, name, XmlWriter._CLOSE_NONE, attributes)
        self._elementStack.append((namespace, name))

    def endTag(self, expectedQualifiedName=None):
        """
        End tag that has been started before using `startTag()`,
        optionally checking that the name matches ``expectedQualifiedName``.

        As example, consider the following writer with a namespace:

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out)
            >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml")

        Now start a couple of elements:

            >>> xml.startTag("html")
            >>> xml.startTag("xhtml:body")

        Try to end a mistyped tag:

            >>> xml.endTag("xhtml:doby")
            Traceback (most recent call last):
                ...
            XmlError: tag name must be xhtml:doby but is xhtml:body

        Try again properly:

            >>> xml.endTag("xhtml:body")

        Try to end another mistyped tag, this time without namespace:

            >>> xml.endTag("xml")
            Traceback (most recent call last):
                ...
            XmlError: tag name must be xml but is html

        End the tag properly, this time without an expected name:

            >>> xml.endTag()

        Try to end another tag without any left:

            >>> xml.endTag()
            Traceback (most recent call last):
                ...
            XmlError: tag stack must not be empty
        """
        scopeToRemove = self._scope()
        try:
            (namespace, name) = self._elementStack.pop()
        except IndexError:
            raise XmlError(u"tag stack must not be empty")
        if expectedQualifiedName:
            # Validate that actual tag name matches expected name.
            uniExpectedQualifiedName = self._unicoded(expectedQualifiedName)
            actualQualifiedName = _joinPossiblyQualifiedName(namespace, name)
            if actualQualifiedName != expectedQualifiedName:
                self._elementStack.append((namespace, name))
                raise XmlError(u"tag name must be %s but is %s" % (uniExpectedQualifiedName, actualQualifiedName))
        if scopeToRemove in self._namespaces:
            del self._namespaces[scopeToRemove]
        self._writeTag(namespace, name, XmlWriter._CLOSE_AT_START)

    def tag(self, qualifiedName, attributes={}):
        uniQualifiedName = self._unicoded(qualifiedName)
        namespace, name = _splitPossiblyQualifiedName(u"tag name", uniQualifiedName)
        self._writeTag(namespace, name, XmlWriter._CLOSE_AT_END, attributes)

    def text(self, text):
        """
        Write ``text`` using escape sequences if needed.

        Using a writer like

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)

        you can write some text:

            >>> xml.text("<this> & <that>")
            >>> print out.getvalue().rstrip("\\r\\n")
            &lt;this&gt; &amp; &lt;that&gt;

        If ``text`` contains line feeds, the will be normalized to `newline()`:

            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)
            >>> xml.startTag("some")
            >>> xml.text("a text\\nwith multiple lines\\n    and indentation and trailing blanks   ")
            >>> xml.endTag()
            >>> print out.getvalue().rstrip("\\r\\n")
            <some>
              a text
              with multiple lines
              and indentation and trailing blanks
            </some>

        Empty text does not result in any output:

            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)
            >>> xml.startTag("some")
            >>> xml.text("")
            >>> xml.endTag()
            >>> print out.getvalue().rstrip("\\r\\n")
            <some>
            </some>
        """
        _validateNotNone(u"text", text)
        uniText = self._unicoded(text)
        if self._pretty:
            for uniLine in StringIO(uniText):
                self._writeIndent()
                uniLine = uniLine.lstrip(" \t").rstrip(" \t\r\n")
                self._writeEscaped(uniLine)
                self.newline()
        else:
            self._writeEscaped(uniText)

    def comment(self, text, embedInBlanks=True):
        """
        Write an XML comment.

        As example set up a writer:

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)

        Now add the comment

            >>> xml.comment("some comment")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <!-- some comment -->

        A comment can spawn multiple lines. If pretty is enabled, the lines
        will be indented. Again, first set up a writer:

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)

        Then add the comment

            >>> xml.comment("some comment\\nspawning mutiple\\nlines")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <!--
            some comment
            spawning mutiple
            lines
            -->
        """
        uniText = self._unicoded(text)
        if not embedInBlanks and not uniText:
            raise XmlError("text for comment must not be empty, or option embedInBlanks=True must be set")
        if u"--" in uniText:
            raise XmlError("text for comment must not contain \"--\"")
        hasNewline = (u"\n" in uniText) or (u"\r" in uniText)
        hasStartBlank = uniText and uniText[0].isspace()
        hasEndBlank = (len(uniText) > 1) and uniText[-1].isspace()
        self._writePrettyIndent()
        self._write(u"<!--");
        if hasNewline:
            if self._pretty:
                self.newline()
            elif embedInBlanks and not hasStartBlank:
                self._write(u" ")
            for uniLine in StringIO(uniText):
                if self._pretty:
                    self._writeIndent()
                self._writeEscaped(uniLine.rstrip("\n\r"))
                self.newline()
            self._writePrettyIndent()
        else:
            if embedInBlanks and not hasStartBlank:
                self._write(u" ")
            self._writeEscaped(uniText)
            if embedInBlanks and not hasEndBlank:
                self._write(u" ")
        self._write(u"-->");
        if self._pretty:
            self.newline()

    def cdata(self, text):
        """
        Write a CDATA section.

        As example set up a writer:

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)

        Now add the CDATA section:

            >>> xml.cdata("some data\\nlines\\n<tag>&&&")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <![CDATA[some data
            lines
            <tag>&&&]]>
        """
        self._rawBlock(u"CDATA section", XmlWriter._CDATA_START, XmlWriter._CDATA_END, text)

    def processingInstruction(self, target, text):
        """
        Write a processing instruction.

        As example set up a writer:

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)

        Now add the processing instruction:

            >>> xml.processingInstruction("xsl-stylesheet", "href=\\"some.xsl\\" type=\\"text/xml\\"")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <?xsl-stylesheet href="some.xsl" type="text/xml"?>
        """
        targetName = u"target for processing instrution"
        _validateNotNone(targetName, text)
        _validateNotEmpty(targetName, text)
        uniFullText = self._unicoded(target)
        if text:
            uniFullText += " "
            uniFullText += self._unicoded(text)
        self._rawBlock(u"processing instruction", XmlWriter._PROCESSING_START, XmlWriter._PROCESSING_END, uniFullText)

    def _rawBlock(self, name, start, end, text):
        _assertIsUnicode("name", name)
        _assertIsUnicode("start", start)
        _assertIsUnicode("end", end)
        _validateNotNone(u"text for %s" % name, text)
        uniText = self._unicoded(text)
        if end in uniText:
            raise XmlError("text for %s must not contain \"%s\"" % (name, end))
        self._writePrettyIndent()
        self._write(start)
        self._write(uniText)
        self._write(end)
        self._writePrettyNewline()

    def raw(self, text):
        """
        Write raw ``text`` without escaping, validation and pretty printing.

        Using a writer like

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)

        you can use ``raw`` for good and add for exmaple a doctype declaration:

            >>> xml.raw("<!DOCTYPE html PUBLIC \\"-//W3C//DTD XHTML 1.0 Transitional//EN\\" \\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\\">")
            >>> print out.getvalue().rstrip("\\r\\n")
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

        but you can also do all sorts of evil things which can invalidate the XML document:

            >>> out = StringIO()
            >>> xml = XmlWriter(out, prolog=False)
            >>> xml.raw(">(^_^)<  not particular valid XML &&&")
            >>> print out.getvalue().rstrip("\\r\\n")
            >(^_^)<  not particular valid XML &&&
        """
        _validateNotNone(u"text", text)
        uniText = self._unicoded(text)
        self._write(uniText)

    def close(self):
        """
        Close the writer, validate that all started elements have ended and
        prevent further output.

        Using a writer like

            >>> from StringIO import StringIO
            >>> out = StringIO()
            >>> xml = XmlWriter(out)

        you can write a tag without closing it:

            >>> xml.startTag("some")

        However, once you try to close the writer, you get:

            >>> xml.close()
            Traceback (most recent call last):
                ...
            XmlError: missing end tags must be added: </some>
        """
        remainingElements = ""
        while self._elementStack:
            if remainingElements:
                remainingElements += ", "
            namespace, name = self._elementStack.pop()
            remainingElements += u"</%s>" % self._elementName(name, namespace)
        if remainingElements:
            raise XmlError(u"missing end tags must be added: %s" % remainingElements)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
