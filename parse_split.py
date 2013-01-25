import urllib2
import abc
import re
import StringIO
import sys
import json

FAQ_LOC = "http://db.gamefaqs.com/console/xbox360/file/infinite_undiscovery.txt"

class ABCParser:
    __metaclass__ = abc.ABCMeta
    terminator = None

    def __init__(self):
        self.io_src = None
        self._buffer = ""
        self.data = ""

    def setiosrc(self, io_src):
        if isinstance(io_src, basestring):
            self.io_src = StringIO.StringIO(io_src)
        else:
            self.io_src = io_src

    def foundterminator(self):
        raise NotImplementedError

    def read(self):
        for _line in self.io_src:
            self._buffer += _line
            if self._buffer.find(self.terminator) > -1:
                self.data = self._buffer
                self._buffer = ""
                self.foundterminator()
        self.data = self._buffer
        self.foundterminator()

class ABCIUParser(ABCParser):
    __metaclass__ = abc.ABCMeta
    seperator_equals = "=" * 79
    seperator_minus = "-" * 79
    itemdata = {}

    def write(self, output_file):
        with open(output_file, "w") as _f:
            json.dump(self.itemdata, _f)

class ABCSectionParser(ABCIUParser):
    __metaclass__ = abc.ABCMeta
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
    header_regex = re.compile(r"\.\)(.*) - G.*\r\n")

    def foundterminator(self):
        if self.in_section: print "SECTION: " + self.section_name
        if self.in_section and self.section_name == "ITEM CREATION LISTS":
            ic = ICSectionParser()
            ic.setiosrc(self.data)
            ic.read()
        self._foundterminatorfinish()

class ICSectionParser(ABCSectionParser):
    terminator = "\r\n{0}\r\n".format(ABCSectionParser.seperator_equals)
    header_regex = re.compile(r"(.*) - .*\r\n")

    def foundterminator(self):
        if self.in_section: print "USER: " + self.section_name
        if self.in_section:
            item = ICItemParser()
            item.setiosrc(self.data)
            item.read()
        self._foundterminatorfinish()

class ICItemParser(ABCIUParser):
    terminator = "\r\n{0}\r\n".format(ABCSectionParser.seperator_minus)
    item_regex = re.compile(r"(.+)\(.+\):(.+)\n(\[ \])?\s+- -", flags=re.DOTALL)
    multiple_regex = re.compile(r"(\d+)x (.+)")

    def foundterminator(self):
        _match = self.item_regex.search(self.data)
        if _match:
            _item = _match.group(1)
            _materials = _match.group(2)
            self.setitemdata(_item, _materials)

    def setitemdata(self, item, materials):
        if item:
            item = item.strip().strip('"')
            if materials:
                materials = [x.strip() for x in materials.splitlines()]
                for each in materials:
                    _tmp = []
                    _match = self.multiple_regex.match(each)
                    if _match:
                        _tmp.append({"num": _match.groups()[0],
                                     "obj": _match.groups()[1]})
                    else:
                        _tmp.append({"num": 1,
                                     "obj": each})
                self.itemdata[item] = { "ic": _tmp}

class IUItems:
    def __init__(self, url):
        self.url = url
        self.parser = SectionParser()

    def parseurl(self):
        if self.url.startswith("http"):
            _f = urllib2.urlopen(self.url)
        else:
            _f = open(self.url, "r")
        try:
            self.parser.setiosrc(_f)
            self.parser.read()
        finally:
            _f.close()

    def writejson(self, output):
        self.parser.write(output)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        i = IUItems(sys.argv[1])
        i.parseurl()
        i.writejson(sys.argv[2])

