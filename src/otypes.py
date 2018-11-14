from src.gameobj import Object, Controllable
from src.weapon import Weapon
from src.cmd_defines import AllCommands as cmds
from src.geometry import Point

class Building(Controllable):
    def __init__(self, sess, coords, ftprint, \
            heal_pts, owner, armor, weapon):
        super().__init__(sess, coords, ftprint, heal_pts, owner, armor, weapon)
        self.otype = 'B'



class Unit(Controllable):
    def __init__(self, sess, coords, ftprint, \
            heal_pts, owner, armor, weapon, speed):
        if speed is None:
            raise ValueError('Unit speed was not specified')
        super().__init__(sess, coords, ftprint, heal_pts, owner, armor, weapon)
        self.speed = speed
        self.dest = self.coords
        self.node = Point(-1, -1)
        self.direction = Point(0, 0)
        self.nodes = []
        self.otype = 'U'
        self.add_cmd('stop', cmds.stop, (1,0))
        self.add_cmd('move', cmds.move, (2,0))

    def update(self, tick):
        super().update(tick)
        points = 0
        while self.coords != self.dest and points < self.speed:
            prev = self.coords.copy()
            self.session.board.release_fp(self)
            self.session.tell_tell_dirty()
            if self._get_direction(self.coords, self.node) != self.direction:
                self.node = self.nodes[0]
                self.nodes = self.nodes[1:]
                self.direction = self._get_direction(self.coords, self.node)
                self.direction_cost = self._get_dir_cost(self.direction)
            points += self.direction_cost
            self.coords = self.coords + self.direction
            self.coords.round(2)
            if not self.session.board.apply_fp(self):
                self.coords = prev
                self.session.board.apply_fp(self)
                self.dest = self.coords.copy()
                self.node = Point(-1, -1)
                self.direction = Point(0, 0)
                self.nodes = []

    def request_path(self):
        self.nodes = self.session.board.request_path( \
            self.footprint, self.coords, self.dest)
        self.node = Point(-1, -1)
        self.direction = Point(0, 0)

    def _get_direction(self, orig, dest):
        dx = (1 if orig.x < dest.x else -1) if orig.x != dest.x else 0
        dy = (1 if orig.y < dest.y else -1) if orig.y != dest.y else 0
        sub_per_cell = self.session.request_subpercell()
        return Point(dx/sub_per_cell, dy/sub_per_cell)

    def _get_dir_cost(self, direction):
        dx, dy = direction.get()
        return 1.4 if (dx != 0 and dy != 0) else 1



class Destructible(Controllable):
    def __init__(self, sess, coords, ftprint, heal_pts, armor):
        super().__init__(sess, coords, ftprint, heal_pts, None, armor, Weapon())
        self.otype = 'D'



class Resource(Object):
    def __init__(self, sess, coords, ftprint, rtype=None, rvalue=None):
        if None in (rtype, rvalue):
            raise ValueError('Resource.type or Resource.value was not specified')
        super().__init__(sess, coords, ftprint)
        self.rtype = rtype
        self.rvalue = rvalue
        self.otype = 'R'

    def get_attrs(self):
        '''Creates dict with data to put in console'''
        d = super().get_attrs()
        d.update({
            'remain': self.rvalue,
        })
        return d
