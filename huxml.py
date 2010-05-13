"""
huxml
====

Huxml is a Python module to create huge XML files with a low memory footprint.

Writing a simple document
-----------------------

The following example creates a very simple XHTML document.

To make it simple, the output goes to a string, but you could also use
a file that has been created using ``open()``.
 
>>> from StringIO import StringIO
>>> out = StringIO()

First create an `XmlWriter` to write the XML code to the specified output:

>>> xml = XmlWriter(out)

Then add the document header:

>>> xml.document()
>>> print out.getvalue().rstrip("\\r\\n")
<xml version="1.0" encoding="utf-8">

Next add the ``<html>`` start element:

>>> xml.startElement(u"html")

Now comes the <body>. To pass attributes, specify them in a dictionary.
So in order to add::

  <body id="top">

use:

>>> xml.startElement(u"body", {u"id":u"top"})

Let' add a little text so there is something to look at:

>>> xml.text(u"Hello world!")
>>> xml.newline()

Wrap it up: close all elements and the document.

>>> xml.endElement()
>>> xml.endElement()
>>> xml.close()

And this is what we get:

>>> print out.getvalue().rstrip("\\r\\n")
<xml version="1.0" encoding="utf-8">
<html>
  <body id="top">
Hello world!
  </body>
</html>

Now the same thing but with a name space. First create the document 
and header like above: 

>>> out = StringIO()
>>> xml = XmlWriter(out)
>>> xml.document()

Next add the namespace:

>>> xml.addNamespace(u"xhtml", u"http://www.w3.org/1999/xhtml")

Now elements can use the optional `namespace` parameter:

>>> xml.startElement(u"html", namespace=u"xhtml")
>>> xml.startElement(u"body", namespace=u"xhtml")
>>> xml.text(u"Hello world!")
>>> xml.newline()
>>> xml.endElement()
>>> xml.endElement()
>>> xml.close()

As a result, element names are now prefixed with "xhtml:":

>>> print out.getvalue().rstrip("\\r\\n")
<xml version="1.0" encoding="utf-8">
<xhtml:html xlmns:xhtml="http://www.w3.org/1999/xhtml">
  <xhtml:body>
Hello world!
  </xhtml:body>
</xhtml:html>

"""
import collections
import os
import xml.sax.saxutils

class XmlError(Exception):
    """
    Error raised when XML can not be generated.
    """
    pass

def _requireUnicode(name, value):
    if not isinstance(value, unicode):
        raise XmlError(u"value for %r must be of type unicode but is: %r" % (name, value))

def quoted(value):
    _requireUnicode(u"value", value)
    return xml.sax.saxutils.quoteattr(value)

class XmlWriter(object):
    _CLOSE_NONE = u"none"
    _CLOSE_AT_START = u"start"
    _CLOSE_AT_END = u"end"

    def __init__(self, output, pretty=True, encoding=u"utf-8", errors=u"strict"):
        assert output is not None
        assert encoding
        _requireUnicode(u"encoding", encoding)
        assert errors
        self._output = output
        self._pretty = pretty
        self._indent = u"  "
        self._newline = unicode(os.linesep, "ascii")
        self._encoding = encoding
        self._errors = errors
        self._namespaces = {}
        self._elementStack = collections.deque()
        self._namespacesToAdd = collections.deque()

    def _encoded(self, text):
        assert text is not None
        _requireUnicode(u"text", text)
        return text.encode(self._encoding, self._errors)

    def _elementName(self, name, namespace):
        assert name
        if namespace:
            result = u"%s:%s" % (namespace, name)
        else:
            result = name
        return result

    def _write(self, text):
        assert text is not None
        _requireUnicode(u"text", text)
        self._output.write(self._encoded(text))

    def newline(self):
        self._write(self._newline)

    def addNamespace(self, name, uri):
        assert name
        _requireUnicode(u"name", name)
        assert uri
        _requireUnicode(u"uri", uri)
        assert not self._elementStack, u"currently namespace must be added before first element"

        if name in self._namespaces:
            raise ValueError(u"namespace %r must added only once but already is %r" % (name, uri))
        self._namespacesToAdd.append((name, uri))

    def document(self):
        self._write(u"<xml version=%s encoding=%s>" %
            (quoted(u"1.0"), quoted(self._encoding))
        )
        self.newline()

    def _writeElement(self, name, close, attributes={}, namespace=None):
        assert name
        _requireUnicode(u"name", name)
        assert close
        assert close in (XmlWriter._CLOSE_NONE, XmlWriter._CLOSE_AT_START, XmlWriter._CLOSE_AT_END)
        assert attributes is not None
        if namespace:
            _requireUnicode(u"namespace", namespace)

        # Process new namespaces to add.
        # FIXME: Do not modify attributes passed, use a copy instead.
        actualAttributes = attributes.copy()
        while self._namespacesToAdd:
            namespaceName, uri = self._namespacesToAdd.pop()
            if namespaceName:
                actualAttributes[u"xlmns:%s" % namespaceName] = uri
            else:
                actualAttributes[u"xlmns"] = uri
            self._namespaces[namespaceName] = uri
        if namespace:
            if namespace not in self._namespaces:
                raise ValueError(u"namespace %r must be added before use" % namespace)
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
            _requireUnicode(u"attribute name", attributeName)
            value = actualAttributes[attributeName]
            _requireUnicode(u"value of attribute %r" % attributeName, value)
            self._write(u" %s=%s" % (attributeName, quoted(value)))
        if close == XmlWriter._CLOSE_AT_END:
            self._write(u"/")
        self._write(u">")
        if self._pretty:
            self.newline()

    def startElement(self, name, attributes={}, namespace=None):
        self._writeElement(name, XmlWriter._CLOSE_NONE, attributes, namespace)
        self._elementStack.append((name, namespace))

    def endElement(self):
        try:
            (name, namespace) = self._elementStack.pop()
        except IndexError:
            raise XmlError(u"element stack must not be empty")
        self._writeElement(name, XmlWriter._CLOSE_AT_START, namespace=namespace)

    def element(self, name, attributes={}, namespace=None):
        self._writeElement(name, XmlWriter._CLOSE_AT_END, attributes, namespace)

    def text(self, text):
        assert text is not None
        _requireUnicode(u"text", text)
        self._write(xml.sax.saxutils.escape(text))

    def close(self):
        remainingElements = ""
        while self._elementStack:
            if remainingElements:
                remainingElements += ", "
            name, namespace = self._elementStack.pop()
            remainingElements += u"</%s>" % self._elementName(name, namespace)
        if remainingElements:
            raise XmlError(u"elements must end: %s" % remainingElements)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
