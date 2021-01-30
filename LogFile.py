from utils import *
from parser import *
import Ngraph


class LogFile:
    def __init__(self, path):
        self.path = path
        self.cache = dict()

    def get_ngraphs(self, n):
        if n in self.cache.keys():
            return self.cache[n]
        result = n_graphs_from_file(self.path, n)
        self.cache[n] = result
        return result

    def write_to_csv(self, out_path, n=None, max_time=5):
        timeout = datetime.timedelta(milliseconds=max_time*100)
        if n is None:
            for item in self.cache.keys():
                self.write_to_csv(out_path, item)
        else:
            if n not in self.cache.keys():
                self.get_ngraphs(n)
            with open(out_path, mode='w') as f:
                f.write(NGraph.CSV_HEADER_ROW + "\n")
                for item in self.cache[n]:
                    if (item.time_taken - timeout).total_seconds() > 0:
                        continue
                    f.write(item.to_csv_line() + "\n")
