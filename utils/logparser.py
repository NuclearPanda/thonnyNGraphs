import json
from objects.ngraph import NGraph
from utils.utils import increment_index, parse_index


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


def n_graphs_from_file(filename, n):
    if n < 2:
        raise NotImplementedError
    graphs = []
    events = get_keystroke_events(read_file(filename))
    for i in range(len(events) - n + 1):
        if increment_index(parse_index(events[i]['index'])) == parse_index(events[i + 1]['index']):
            current = NGraph.from_events(events[i], events[i + 1])
            for j in range(n - 1):
                if parse_index(events[i + j + 1]['index']) == increment_index(current.end_index):
                    current.append_event(events[i + j + 1])
            if current.n == n:
                graphs.append(current)
    return graphs
