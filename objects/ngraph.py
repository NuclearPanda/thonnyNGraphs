import datetime

import utils.utils as util


class NGraph:

    def __init__(self, keystrokes: str, start_time: datetime, end_time: datetime, start_index, end_index):
        self.name = keystrokes
        self.n = len(keystrokes)
        self.start_time = start_time
        self.end_time = end_time
        self.time_taken = end_time - start_time
        self.start_index = util.parse_index(start_index)
        self.end_index = util.parse_index(end_index)

    def append(self, key, new_end_time, new_end_index):
        self.name += key
        self.end_time = new_end_time
        self.end_index = new_end_index
        self.recalculate_time_taken()

    def append_event(self, event):
        self.name += event['text']
        self.n += len(event['text'])
        self.end_time = util.parse_date(event['time'])
        self.end_index = util.parse_index(event['index'])
        self.recalculate_time_taken()

    def recalculate_time_taken(self):
        self.time_taken = self.end_time - self.start_time

    def to_list(self) -> list:
        return [self.name, self.n, self.start_time, self.end_time, self.time_taken.total_seconds(), self.start_index,
                self.end_index]


    @staticmethod
    def from_events(event1, event2):
        return NGraph(event1['text'] + event2['text'], util.parse_date(event1['time']), util.parse_date(event2['time']),
                      event1['index'], event2['index'])

    def __str__(self):
        return "NGraph( name = '" + self.name + "'" + \
               ", n = " + str(self.n) + \
               ", start_aeg = " + str(self.start_time) + \
               ", lõpp_time = " + str(self.end_time) + \
               ", aeg = " + str(self.time_taken) + \
               ", start_index = " + str(self.start_index) + \
               ", lõpp_index = " + str(self.end_index)
