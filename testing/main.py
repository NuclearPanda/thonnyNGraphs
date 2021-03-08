from objects.logfile import LogFile
import pandas as pd

log = LogFile('../data/log2_1.txt')

ngraphs = log.get_ngraphs(2)


csv = pd.read_csv('../test.csv')
print(csv['ngraph'].value_counts())
print()
values = csv[['ngraph', 'time_taken']].groupby(csv['ngraph']).mean().sort_values('time_taken', ascending=False)
print(values)

