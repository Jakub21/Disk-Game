import itertools, heapq

class Queue:
    '''Priority Heap Implementation'''
    def __init__(self):
        self.elems = []
        self.counter = itertools.count()
        self._all = []

    def add(self, coords, cell=0, heuristics=0):
        x, y = coords
        priority = cell + heuristics
        entry = (priority, next(self.counter), coords)
        heapq.heappush(self.elems, entry)
        self._all += [coords]

    def add_many(self, elems):
        for el in elems:
            self.add(el)

    def pop(self):
        if self.elems:
            priority, count, task = heapq.heappop(self.elems)
            return task
        raise KeyError('Queue is empty')

    def is_empty(self):
        return len(self.elems) == 0

    def get_len(self):
        return len(self.elems)

    def set_empty(self):
        while not self.is_empty():
            self.pop()
