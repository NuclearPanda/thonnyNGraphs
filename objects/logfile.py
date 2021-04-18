import pandas as pd

import utils.logparser as parser


class LogFile:
    def __init__(self, path):
        self.path = path
        self.cache = dict()

    def get_ngraphs(self, n) -> pd.DataFrame:
        if n in self.cache.keys():
            return self.cache[n]
        result = parser.n_graphs_from_file(self.path, n)
        for i in range(len(result)):
            result[i] = result[i].to_list()

        df = pd.DataFrame(result,
                          columns=["n-graaf", "n", "start_aeg", "lõpp_aeg", "aeg", "start_index", "lõpp_index"])

        self.cache[n] = df
        return df
