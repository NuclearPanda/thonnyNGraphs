import datetime


def parse_date(time_str):
    return datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')


def increment_index(index: tuple):
    return index[0], index[1] + 1


def parse_index(in_str: str):
    split = in_str.split('.')
    return int(split[0]), int(split[1])
