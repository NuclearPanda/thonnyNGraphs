import datetime

from typing import List

import utils.logparser as parser
from objects.ngraph import NGraph


class LogFile:
    def __init__(self, path):
        self.path = path
        self.cache = dict()

    def get_ngraphs(self, n) -> List[NGraph]:  # return a list of ngraphs
        if n in self.cache.keys():
            return self.cache[n]
        result = parser.n_graphs_from_file(self.path, n)
        self.cache[n] = result
        return result

    def write_to_csv_path(self, out_path, n=None, max_time=5):
        timeout = datetime.timedelta(milliseconds=max_time * 100)
        if n is None:
            for item in self.cache.keys():
                self.write_to_csv_path(out_path, item)
        else:
            if n not in self.cache.keys():
                self.get_ngraphs(n)
            with open(out_path, mode='w', encoding='utf8') as f:
                f.write(NGraph.CSV_HEADER_ROW + "\n")
                for item in self.cache[n]:
                    if (item.time_taken - timeout).total_seconds() > 0:
                        continue
                    f.write(item.to_csv_line() + "\n")

    def write_to_csv_file(self, out_file, n=None, max_time=5):
        timeout = datetime.timedelta(milliseconds=max_time * 100)
        if n is None:
            for item in self.cache.keys():
                self.write_to_csv_file(out_file, item)
        else:
            if n not in self.cache.keys():
                self.get_ngraphs(n)

            out_file.write(NGraph.CSV_HEADER_ROW + "\n")
            for item in self.cache[n]:
                if (item.time_taken - timeout).total_seconds() > 0:
                    continue
                out_file.write(item.to_csv_line() + "\n")

    def to_table_format(self, n):
        out = {}
        data = self.get_ngraphs(n)
        for i, item in enumerate(data):
            out[i] = item.to_table_entry()
        return out
