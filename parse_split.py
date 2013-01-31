import urllib2
import abc
import re
import StringIO
import argparse
import json
import logging

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
    logger = logging.getLogger("SplitParser")

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
        if self.in_section: self.logger.info("Parsing section [ {0} ]".format(self.section_name))
        if self.in_section and self.section_name == "ITEM CREATION LISTS":
            ic = ICSectionParser()
            ic.setiosrc(self.data)
            ic.read()
        self._foundterminatorfinish()

class ICSectionParser(ABCSectionParser):
    terminator = "\r\n{0}\r\n".format(ABCSectionParser.seperator_equals)
    header_regex = re.compile(r"(.*) - .*\r\n")

    def foundterminator(self):
        if self.in_section: self.logger.info("==> Parsing user [ {0} ]".format(self.section_name))
        if self.in_section and self.section_name != "CAPELL":
            item = ICItemParser()
            item.setiosrc(self.data)
            item.read()
        self._foundterminatorfinish()

class ICItemParser(ABCIUParser):
    terminator = "\r\n{0}\r\n".format(ABCSectionParser.seperator_minus)
    item_regex = re.compile(r"(.+)\(.+\):(.+)\n(\[ \])?\s+- -", flags=re.DOTALL)
    multiple_regex = re.compile(r"(\d+)x (.+)")
    error_corrections = {"Hearthstone Neclace": "Hearthstone Necklace",
                         "Thousand Year Old Sigh": "Thousand Year Sigh",
                         "Cactis Needle": "Cactus Needle"}

    def foundterminator(self):
        _match = self.item_regex.search(self.data)
        if _match:
            _item = _match.group(1)
            _materials = _match.group(2)
            self.setitemdata(_item, _materials)

    def _error_correct(self, item):
        if self.error_corrections.has_key(item):
            return self.error_corrections.get(item)
        else:
            return item

    def setitemdata(self, item, materials):
        if item:
            item = item.strip().strip('"')
            item = self._error_correct(item)
            if materials:
                materials = [x.strip().strip('"') for x in materials.splitlines()]
                _tmp = []
                for each in materials:
                    _num = 1
                    _obj = self._error_correct(each)
                    _match = self.multiple_regex.match(each)
                    if _match:
                        _num = _match.groups()[0]
                        _obj = self._error_correct(_match.groups()[1])
                    _tmp.append({"num": _num, "obj": _obj})
                self.itemdata[item] = { "ic": _tmp}

class ParseSplit:
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
    parser = argparse.ArgumentParser(description="Parse Split Infinity's Infinite Undiscovery FAQ IC items into JSON",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--faqpath", default=FAQ_LOC, help="local or remote location of Split Infinity's Infinite Undiscovery FAQ. If you use an argument that starts with http, we assume it's a web location; otherwise it's treated as a local file name")
    parser.add_argument("jsonoutput", help="file to output IC items in JSON format")
    parser.add_argument("--debug", default=False)

    args = parser.parse_args()

    if args.debug:
        llevel = logging.DEBUG
    else:
        llevel = logging.INFO

    logging.basicConfig(format="%(message)s", level=llevel)

    ps = ParseSplit(args.faqpath)
    ps.parseurl()
    ps.writejson(args.jsonoutput)

