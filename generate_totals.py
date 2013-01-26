import argparse
import json
import logging

ITEMS_DB = "iuitems.json"

class GenerateItems:
    def __init__(self, item_db_file, needed_items_file):
        self.item_db_file = item_db_file
        self.needed_items_file = needed_items_file
        self.items_db = {}
        self.needed_items = []

    def _loaditemsdb(self):
        with open(self.item_db_file, "r") as f:
            self.items_db = json.load(f)

    def _loadneededitems(self):
        self.needed_items = []
        with open(self.needed_items_file, "r") as f:
            for _line in f:
                self.needed_items.append(_line.strip())

    def test(self):
        self._loaditemsdb()
        self._loadneededitems()
        for item in self.needed_items[:5]:
            deps = self.items_db.get(item, "Item [ {0} ] not found".format(item))
            print "{0}: {1}".format(item, deps.get('ic'))

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
    gi.test()

