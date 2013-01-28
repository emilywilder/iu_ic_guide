import argparse
import json
import logging

ITEMS_DB = "iuitems.json"

class GenerateItems:
    def __init__(self, item_db_file, needed_items_file, obtained_items_file=None):
        self.logger = logging.getLogger("GenerateItems")
        self.item_db_file = item_db_file
        self.needed_items_file = needed_items_file
        self.obtained_items_file = obtained_items_file
        self.items_db = {}
        self.needed_items = {}
        self.obtained_items = {}
        self.notfound_items = []
        self.materials = {}

    def _loaditemsdb(self):
        with open(self.item_db_file, "r") as f:
            self.items_db = json.load(f)

    def _loadneededitems(self):
        self.needed_items = {}
        with open(self.needed_items_file, "r") as f:
            for _line in f:
                (_num, _obj) = _line.strip().split('|')
                self.needed_items[_obj] = int(_num)

    def _loadobtaineditems(self):
        self.obtained_items = {}
        if self.obtained_items_file:
            with open(self.obtained_items_file, "r") as f:
                for _line in f:
                    (_num, _obj) = _line.strip().split('|')
                    self.obtained_items[_obj] = int(_num)

    def _loaddata(self):
        self._loaditemsdb()
        self._loadneededitems()
        self._loadobtaineditems()

    def aggregate(self, recursive=False):
        self._loaddata()
        self._aggregate(self._itericdeps(), recursive)

    def _itericdeps(self):
        for _obj, _num in self.needed_items.items():
            if self.items_db.has_key(_obj):
                for i in xrange(_num):
                    for rec in self.items_db.get(_obj).get("ic"):
                        yield rec
            else:
                self.notfound_items.append(_obj)

    def _storematerial(self, item):
        if self.materials.has_key(item.get("obj")):
            self.materials[item.get("obj")] += int(item.get("num"))
        else:
            self.materials[item.get("obj")] = int(item.get("num"))

    def _aggregate(self, dataset, recursive=False):
        for dep in dataset:
            left = self.obtained_items.get(dep.get("obj"), 0) - int(dep.get("num"))
            self.obtained_items[dep.get("obj")] = max(0, left)
            if left < 0:
                dep = {"num": abs(left), "obj": dep.get("obj")}
            else:
                dep = {"num": 0, "obj": dep.get("obj")}
            if recursive and self.items_db.has_key(dep.get("obj")):
                rec = self.items_db.get(dep.get("obj")).get("ic")
                for i in xrange(int(dep.get("num"))):
                    self._aggregate(rec, recursive)
            else:
                if dep.get("num") > 0:
                    self._storematerial(dep)

    def report(self):
        for item in sorted(self.notfound_items):
            self.logger.debug("[ {0} ] not found in items db".format(item))
        for k, v in sorted(self.materials.items()):
            self.logger.info("{0}: {1}".format(k, v))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve items needed for IC",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--itemdb", default=ITEMS_DB,
                        help="file of IC items in JSON format")
    parser.add_argument("--obtaineditems", help="file of items already obtained")
    parser.add_argument("--recursive", action="store_true", default=False,
                        help="aggregate totals recursively")
    parser.add_argument("neededitems", help="file of items needed")

    args = parser.parse_args()

    if args.debug:
        llevel = logging.DEBUG
    else:
        llevel = logging.INFO

    logging.basicConfig(format="%(message)s", level=llevel)

    gi = GenerateItems(args.itemdb, args.neededitems, args.obtaineditems)
    gi.aggregate(recursive=args.recursive)
    gi.report()

