from objects.logfile import LogFile
import pandas as pd

log = LogFile('../data/log2_1.txt')

ngraphs = log.get_ngraphs(2)

