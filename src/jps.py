from scipy.ndimage.morphology import binary_dilation as dilate
from numpy import array
from src.queue import Queue

class FoundPath(Exception):
    '''Raised when dest is found
    Exception is used to immediatelly leave recursion
    '''



class Pathfinder:
    '''Path-finder class. Implemets jump-point search algorithm.'''
    def __init__(self, board):
        self.size = board.size
        width, height = board.size
        self._field = array([[0 if board.get((x,y)).crossable and \
            board.get((x,y)).occupied < 2 else -1 for x in range(width)] \
            for y in range(height)])

    def find(self, fp, orig, dest):
        orig, dest = orig.get(), dest.get()
        self.field = self._field.copy()
        self.field = dilate(self.field, fp.get_morph_kernel()).astype(int)
        self.field[self.field == 1] = -1
        f = self.field
        if self.acheck(f, dest):
            dest = self._find_nearest_free(f, dest)
        self.orig, self.dest = orig, dest
        self.queue = Queue()
        self.queue.add(orig)
        self.sources = self.amake_2d(None, self.size)
        s = self.sources
        self.aset(f, self.dest, -3)
        self.aset(s, self.orig, -2)
        all_cards = [(0,1), (1,0), (-1,0), (0,-1)]
        all_diags = [(1,1), (1,-1), (-1,1), (-1,-1)]
        self.checked = []
        while not self.queue.is_empty():
            current = self.queue.pop()
            if current in self.checked:
                continue
            self.checked += [current]
            try:
                for delta in all_cards:
                    if not self._is_bwds(self.aget(s, current), current, delta):
                        self._expand_card(current, delta)
                for delta in all_diags:
                    if not self._is_bwds(self.aget(s, current), current, delta):
                        self._expand_diag(current, delta)
            except FoundPath:
                break
        nodes = self._find_nodes()
        return nodes #self._reconstruct(nodes)

    def _find_nearest_free(self, field, coords):
        xx, yy = point
        r = 0
        while True:
            r += 1
            for y in range(yy-r, yy+r+1):
                for x in range(xx-r, xx+r+1):
                    if not self.acheck(field, (x,y)):
                        if self.ain_bounds(field, (x,y)):
                            return x, y

    def _expand_card(self, coords, delta):
        f = self.field
        s = self.sources
        current = coords
        cost = self.aget(f, coords)
        delta_x, delta_y = delta
        while True:
            cost += 1
            cx, cy = current
            current = cx + delta_x, cy + delta_y
            cx, cy = current
            if current == self.dest:
                self.aset(s, current, coords)
                raise FoundPath()
            if self.acheck(f, current):
                return False
            prev_cost = self.aget(f, current)
            if prev_cost < cost and prev_cost != 0:
                return
            self.aset(s, current, coords)
            self.aset(f, current, cost)
            # Check forced neighbours
            u, b =  self.acheck(f, (cx, cy-1)), self.acheck(f, (cx, cy+1))
            du = self.acheck(f, (cx+delta_x, cy-1))
            db = self.acheck(f, (cx+delta_x, cy+1))
            l, r = self.acheck(f, (cx-1, cy)), self.acheck(f, (cx+1, cy))
            dl = self.acheck(f, (cx-1, cy+delta_y))
            dr = self.acheck(f, (cx+1, cy+delta_y))
            if current != coords and current != self.aget(s, coords):
                if delta_y == 0 and ((u and not du) or (b and not db)):
                    self.queue.add(current)
                    return True
                if delta_x == 0 and ((l and not dl) or (r and not dr)):
                    self.queue.add(current)
                    return True

    def _expand_diag(self, coords, delta):
        f = self.field
        s = self.sources
        current = coords
        cost = self.aget(f, coords)
        delta_x, delta_y = delta
        while True:
            cost += 1.4
            cx, cy = current
            current = cx + delta_x, cy + delta_y
            cx, cy = current
            if current == self.dest:
                self.aset(s, current, coords)
                raise FoundPath()
            if self.acheck(f, current):
                return False
            prev_cost = self.aget(f, current)
            if prev_cost < cost and prev_cost != 0:
                return
            self.aset(s, current, coords)
            self.aset(f, current, cost)
            # Card jumps
            if self._expand_card(current, (delta_x, 0)):
                self.queue.add(current)
            if self._expand_card(current, (0, delta_y)):
                self.queue.add(current)
            # Check forced neighbours
            s1 = self.acheck(f, (cx-delta_x, cy))
            s2 = self.acheck(f, (cx, cy-delta_y))
            d1 = self.acheck(f, (cx-delta_x, cy+delta_y))
            d2 = self.acheck(f, (cx+delta_x, cy-delta_y))
            if (s1 and not d1) or (s2 and not d2):
                self.queue.add(current)

    def _find_nodes(self):
        s = self.sources
        result = []
        current = self.dest
        while current != self.orig:
            result += [current]
            current = self.aget(s, current)
        return result[::-1]

    def _reconstruct(self, nodes):
        if nodes == []:
            return []
        result = []
        for i in range(len(nodes)-1):
            current = nodes[i]
            _next = nodes[i+1]
            result += [current]
            delta_x, delta_y = self._find_delta(current, _next)
            while current != _next:
                cx, cy = current
                current = cx+delta_x, cy+delta_y
                result += [current]
        return result

    @staticmethod
    def _find_delta(pta, ptb):
        xa, ya = pta
        xb, yb = ptb
        dx = (1 if xa < xb else -1) if xa != xb else 0
        dy = (1 if ya < yb else -1) if ya != yb else 0
        return dx, dy

    @staticmethod
    def _is_bwds(pta, ptb, delta):
        '''Check if when moving along delta from pta, ptb is right behind'''
        if pta == -2: return False # Nothing is backwards. Used for orig pt
        try: xa, ya = pta
        except:
            raise ValueError('Could not unpack {}, expected 2-tuple'.format(pta))
        xb, yb = ptb
        delta_x, delta_y = delta
        dx = (1 if xa < xb else -1) if xa != xb else 0
        dy = (1 if ya < yb else -1) if ya != yb else 0
        if delta_x == -dx and delta_y == -dy:
            return True
        return False

    ################################
    # Array-related helper methods

    def ain_bounds(self, field, coords):
        h, w = field.shape
        x, y = coords
        return (y >= 0 and y < h and x >= 0 and x < w)

    def acheck(self, field, coords, value=-1):
        if not self.ain_bounds(field, coords):
            return True
        h, w = field.shape
        x, y = coords
        return field[int(y), int(x)] == value

    def aget(self, field, coords):
        x, y = coords
        if not self.ain_bounds(field, coords):
            return -1
        return field[int(y), int(x)]

    def aset(self, field, coords, value):
        x, y = coords
        if not self.ain_bounds(field, coords):
            return
        field[int(y), int(x)] = value

    def amake_2d(self, fill, size):
        w, h = size
        return array([[fill for x in range(w)] for y in range(h)])
