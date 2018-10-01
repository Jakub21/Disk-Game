from scipy.ndimage.morphology import binary_dilation as dilate
import numpy as np
from src.queue import Queue

from datetime import datetime

import logging
Log = logging.getLogger('MainLogger')

class FoundPath(Exception):
    '''Raised when goal is found
    Exception is used to immediatelly leave recursion
    '''



class Finder:
    '''Path-finder class. Implemets jump-point search algorithm'''
    def __init__(self, board):
        self.board = board

    def find(self, field, size, fp, orig, goal):
        _set, get, check = self._set, self.get, self.check
        orig, goal = orig.get(), goal.get()
        self.field = field.copy()
        self.field = dilate(self.field, fp).astype(int)
        self.field[self.field == 1] = -1
        f = self.field
        if check(f, goal):
            goal = self._find_nearest_clear(f, goal)
        self.orig, self.goal = orig, goal
        self.size = size
        self.queue = Queue()
        self.queue.add(orig)
        self.sources = self.get_2d(None, self.size)
        s = self.sources
        _set(f, self.goal, -3)
        _set(s, self.orig, -2)
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
                    if not self._is_bwds(get(s,current),current,delta):
                        self._exp_card(current, delta)
                for delta in all_diags:
                    if not self._is_bwds(get(s,current),current,delta):
                        self._exp_diag(current, delta)
            except FoundPath:
                break
        nodes = self._find_nodes()
        return goal, self._reconstruct(nodes)

    def _find_nearest_clear(self, field, point):
        Log.debug('Goal cell has an obstacle, looking for nearest clear cell')
        xx, yy = point
        r = 0
        while True:
            r += 1
            for y in range(yy-r, yy+r+1):
                for x in range(xx-r, xx+r+1):
                    if not self.check(field,(x,y)):
                        if self.in_bounds(field, (x,y)): return (x, y)

    def _exp_card(self, point, delta):
        #Log.debug('Card {} from {}'.format(delta, point))
        _set, get, check = self._set, self.get, self.check
        f = self.field
        s = self.sources
        current = point
        cost = get(f, point)
        delta_x, delta_y = delta
        while True:
            cost += 1
            cx, cy = current
            current = cx+delta_x, cy+delta_y
            cx, cy = current # TODO: Check
            if current == self.goal:
                _set(s, current, point)
                raise FoundPath()
            if check(f, current):
                return False
            prev_cost = get(f, current)
            if prev_cost < cost and prev_cost != 0:
                return # TODO: Check if can return at this point
            _set(s, current, point)
            _set(f, current, cost)
            # Check forced neighbours
            u, b = check(f,(cx,cy-1)), check(f,(cx,cy+1))
            du = check(f,(cx+delta_x,cy-1))
            db = check(f,(cx+delta_x,cy+1))
            l, r = check(f,(cx-1,cy)), check(f,(cx+1,cy))
            dl = check(f,(cx-1,cy+delta_y))
            dr = check(f,(cx+1,cy+delta_y))
            if current != point and current != get(s, point):
                if delta_y == 0 and ((u and not du) or (b and not db)):
                    self.queue.add(current)
                    return True
                if delta_x == 0 and ((l and not dl) or (r and not dr)):
                    self.queue.add(current)
                    return True

    def _exp_diag(self, point, delta):
        #Log.debug('Diag {} from {}'.format(delta, point))
        _set, get, check = self._set, self.get, self.check
        f = self.field
        s = self.sources
        current = point
        cost = get(f, point)
        delta_x, delta_y = delta
        while True:
            cost += 1.7 # Replaced sqrt(2)
            cx, cy = current
            current = cx+delta_x, cy+delta_y
            cx, cy = current # TODO: Check
            if current == self.goal:
                _set(s, current, point)
                raise FoundPath()
            if check(f, current):
                return False
            prev_cost = get(f, current)
            if prev_cost < cost and prev_cost != 0:
                return # TODO: Check if can return at this point
            _set(s, current, point)
            _set(f, current, cost)
            # Card jumps
            if self._exp_card(current, (delta_x, 0)):
                self.queue.add(current)
            if self._exp_card(current, (0, delta_y)):
                self.queue.add(current)
            # Check forced neighbours
            s1, s2 = check(f,(cx-delta_x,cy)), check(f,(cx,cy-delta_y))
            d1 = check(f,(cx-delta_x,cy+delta_y))
            d2 = check(f,(cx+delta_x,cy-delta_y))
            if (s1 and not d1) or (s2 and not d2):
                self.queue.add(current)

    def _find_nodes(self):
        s = self.sources
        result = []
        current = self.goal
        while current != self.orig:
            result += [current]
            current = self.get(s, current)
        result += [self.orig]
        return result[::-1]

    def _reconstruct(self, nodes):
        if nodes == []: return []
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
        dx, dy = 0, 0
        if xa != xb: dx = 1 if xa < xb else -1
        if ya != yb: dy = 1 if ya < yb else -1
        return dx, dy

    @staticmethod
    def _is_bwds(pta, ptb, delta):
        '''Check if when moving along delta from pta, ptb is right behind'''
        if pta == -2: return False # Nothing is backwards (used for orig pt)
        try:
            xa, ya = pta
        except:
            Log.debug('Error at unpacking {}'.format(pta))
            raise
        xb, yb = ptb
        dx, dy = 0, 0
        delta_x, delta_y = delta
        if xa != xb: dx = 1 if xa < xb else -1
        if ya != yb: dy = 1 if ya < yb else -1
        if delta_x == -dx and delta_y == -dy: return True
        return False

    ###############################
    # TODO: Convert this to separate class if it would not affect performance
    # A new instance of this class would be made at every new move command [?]
    # Field-array related methods

    @staticmethod
    def in_bounds(array, point):
        h, w = array.shape
        x, y = point
        return (y >= 0 and y < h and x >= 0 and x < w)

    @staticmethod
    def check(array, point, val=-1):
        '''Function for 2D array: Check value'''
        h, w = array.shape
        x, y = point
        if not(y >= 0 and y < h and x >= 0 and x < w):
            return False # Not in bounds
        return array[y, x] == val

    @staticmethod
    def get(array, point):
        '''Function for 2D array: Get value'''
        h, w = array.shape
        x, y = point
        if not(y >= 0 and y < h and x >= 0 and x < w):
            return 0 # Not in bounds
        return array[y, x]

    @staticmethod
    def _set(array, point, value):
        '''Function for 2D array: Set value'''
        h, w = array.shape
        x, y = point
        if not(y >= 0 and y < h and x >= 0 and x < w):
            return # Not in bounds
        array[y, x] = value

    @staticmethod
    def get_2d(fill, size):
        w, h = size
        return np.array([[fill for x in range(w)] for y in range(h)])
