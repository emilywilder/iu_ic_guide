import urllib2
import abc
import re
import StringIO
import sys

FAQ_LOC = "http://db.gamefaqs.com/console/xbox360/file/infinite_undiscovery.txt"

class ABCParser:
    __metaclass__ = abc.ABCMeta
    terminator = None

    def __init__(self, io_obj):
        if isinstance(io_obj, basestring):
            io_obj = StringIO.StringIO(io_obj)
        self.io_obj = io_obj
        self._buffer = ""
        self.data = ""

    def foundterminator(self):
        raise NotImplementedError

    def read(self):
        for _line in self.io_obj:
            self._buffer += _line
            if self._buffer.find(self.terminator) > -1:
                self.data = self._buffer
                self._buffer = ""
                self.foundterminator()
        self.data = self._buffer
        self.foundterminator()

class ABCIUParser(ABCParser):
    seperator_equals = "=" * 79
    seperator_minus = "-" * 79

class ABCSectionParser(ABCIUParser):
    terminator = None
    header_regex = None
    in_section = False
    in_section_header = False
    section_name = ""

    def _foundterminatorfinish(self):
        if self.in_section_header:
            self.readsectionname()
            self.in_section = True
            self.in_section_header = False
        else:
            self.in_section = False
            self.in_section_header = True

    def readsectionname(self):
        _match = self.header_regex.search(self.data)
        if _match:
            self.section_name = _match.group(1).strip()

class SectionParser(ABCSectionParser):
    terminator = "\r\n{0}\r\n{0}\r\n".format(ABCSectionParser.seperator_equals)
    header_regex = re.compile("\.\)(.*) - G.*\r\n")

    def foundterminator(self):
        if self.in_section: print "SECTION: " + self.section_name
        if self.in_section and self.section_name == "ITEM CREATION LISTS":
            print "in ic section"
            ic = ICSectionParser(self.data)
            ic.read()
        self._foundterminatorfinish()

class ICSectionParser(ABCSectionParser):
    terminator = "\r\n{0}\r\n".format(ABCSectionParser.seperator_equals)
    header_regex = re.compile("(.*) - .*\r\n")

    def foundterminator(self):
        if self.in_section: print "USER: " + self.section_name
        if self.in_section:
            item = ICItemParser(self.data)
            item.read()
        self._foundterminatorfinish()

class ICItemParser(ABCIUParser):
    terminator = "\r\n{0}\r\n".format(ABCSectionParser.seperator_minus)
    item_regex = re.compile("(.+)\(.+\):(.+)\n(\[ \])?\s+- -", flags=re.DOTALL)

    def foundterminator(self):
        _match = self.item_regex.search(self.data)
        if _match:
            _item = _match.group(1)
            _materials = _match.group(2)
            if _item: _item = _item.strip()
            if _materials:
                _materials = [x.strip() for x in _materials.splitlines()]
            print "Item: {0}, Materials: {1}".format(_item, _materials)

class IUItems:
    def __init__(self, url):
        self.url = url

    def parseurl(self):
        if self.url.startswith("http"):
            _f = urllib2.urlopen(self.url)
        else:
            _f = open(self.url, "r")
        try:
            _sp = SectionParser(_f)
            _sp.read()
        finally:
            _f.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        i = IUItems(sys.argv[1])
        i.parseurl()

