import argparse
import json
import logging

ITEMS_DB = "iuitems.json"

class GenerateItems:
    def __init__(self, item_db_file, needed_items_file):
        self.logger = logging.getLogger("GenerateItems")
        self.item_db_file = item_db_file
        self.needed_items_file = needed_items_file
        self.items_db = {}
        self.needed_items = []
        self.materials = {}

    def _loaditemsdb(self):
        with open(self.item_db_file, "r") as f:
            self.items_db = json.load(f)

    def _loadneededitems(self):
        self.needed_items = []
        with open(self.needed_items_file, "r") as f:
            for _line in f:
                (_num, _obj) = _line.strip().split('|')
                self.needed_items.append({"num": _num, "obj": _obj})

    def _loaddata(self):
        if not self.items_db: self._loaditemsdb()
        if not self.needed_items: self._loadneededitems()

    def aggregate(self):
        self._loaddata()
        self._aggregate()

    def _itericdeps(self):
        for item in self.needed_items:
            if self.items_db.has_key(item.get("obj")):
                for i in xrange(int(item.get("num"))):
                    for rec in self.items_db.get(item.get("obj")).get("ic"):
                        yield rec

    def _storematerial(self, item):
        if self.materials.has_key(item.get("obj")):
            self.materials[item.get("obj")] += int(item.get("num"))
        else:
            self.materials[item.get("obj")] = int(item.get("num"))

    def _aggregate(self):
        for dep in self._itericdeps():
            self._storematerial(dep)

    def recur_aggregate(self):
        self._loaddata()
        self._recur_aggregate(self._itericdeps())

    def _recur_aggregate(self, dataset):
        for dep in dataset:
            if self.items_db.has_key(dep.get("obj")):
                rec = self.items_db.get(dep.get("obj")).get("ic")
                self._recur_aggregate(rec)
            else:
                self._storematerial(dep)

    def report(self):
        for k, v in sorted(self.materials.items()):
            self.logger.info("{0}: {1}".format(k, v))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve items needed for IC",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", default=False)
    parser.add_argument("--itemdb", default=ITEMS_DB,
                        help="file of IC items in JSON format")
    parser.add_argument("neededitems", help="file of items needed")

    args = parser.parse_args()

    if args.debug:
        llevel = logging.DEBUG
    else:
        llevel = logging.INFO

    logging.basicConfig(format="%(message)s", level=llevel)

    gi = GenerateItems(args.itemdb, args.neededitems)
    gi.recur_aggregate()
    gi.report()

