from LogFile import LogFile
import parser
import pandas as pd

log = LogFile('data/log2_1.txt')

ngraphs = log.get_ngraphs(2)

log.write_to_csv("test.csv", n=2)

csv = pd.read_csv('test.csv')
print(csv['ngraph'].value_counts())
print()
print(csv[['ngraph', 'time_taken']].groupby(csv['ngraph']).mean().sort_values('time_taken', ascending=False))