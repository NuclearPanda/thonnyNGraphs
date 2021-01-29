import json
import datetime


class NGraph:
    def __init__(self, keystrokes: str, start_time: datetime, end_time: datetime, start_index, end_index):
        self.name = keystrokes
        self.n = len(keystrokes)
        self.start_time = start_time
        self.end_time = end_time
        self.time_taken = end_time - start_time
        self.start_index = start_index
        self.end_index = end_index

    def append(self, key, new_end_time, new_end_index):
        self.name += key
        self.end_time = new_end_time
        self.end_index = new_end_index
        self.recalculate_time_taken()

    def append_event(self, event):
        self.name += event['text']
        self.n += len(event['text'])
        self.end_time = parse_date(event['time'])
        self.end_index = event['index']
        self.recalculate_time_taken()

    def recalculate_time_taken(self):
        self.time_taken = self.end_time - self.start_time

    @staticmethod
    def from_events(event1, event2):
        return NGraph(event1['text'] + event2['text'], parse_date(event1['time']), parse_date(event2['time']),
                      event1['index'], event2['index'])

    def __str__(self):
        return "NGraph( name = '" + self.name + "'" + \
               ", n = " + str(self.n) + \
               ", start_time = " + str(self.start_time) + \
               ", end_time = " + str(self.end_time) + \
               ", time_taken = " + str(self.time_taken) + \
               ", start_index = " + str(self.start_index) + \
               ", end_index = " + str(self.end_index)


def read_file(filename):
    with open(filename) as f:
        data = f.read()
        log = json.loads(data)
    return log


def get_keystroke_events(log, include_pastes=False):
    out = []
    for event in log:
        if event['sequence'] == 'TextInsert' and event['text_widget_class'] == 'CodeViewText':
            if include_pastes:
                out.append(event)
            else:
                if len(event['text']) == 1:
                    out.append(event)
    return out


def parse_date(time_str):
    return datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')


def increment_index(index):
    return round(float(index) + 0.1, 3)


def n_graphs_from_file(filename, n):
    if n < 2:
        raise NotImplementedError
    graphs = []
    events = get_keystroke_events(read_file(filename))
    for i in range(len(events) - n + 1):
        if increment_index(events[i]['index']) == float(events[i + 1]['index']):
            current = NGraph.from_events(events[i], events[i + 1])
            for j in range(n - 1):
                if float(events[i + j + 1]['index']) == increment_index(current.end_index):
                    current.append_event(events[i + j + 1])
            if current.n == n:
                graphs.append(current)
    # if prev is not None and round(float(prev['index']) + 0.1, 3) == round(float(i['index']), 3):
    #    print(prev, i)
    #    graphs.append(NGraph(prev['text'] + i['text'], parse_date(prev['time']), parse_date(i['time'])))
    # prev = i
    return graphs


for a in n_graphs_from_file("data/log3.txt", 2):
    print(a)
