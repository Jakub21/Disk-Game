from src.gameobj import Object, Controllable
from src.weapon import Weapon

class Building(Controllable):
    def __init__(self, sess, coords, ftprint, \
            heal_pts, owner, armor, weapon):
        super().__init__(sess, coords, ftprint, heal_pts, owner, armor, weapon)
        self.otype = 'B'



class Unit(Controllable):
    def __init__(self, sess, coords, ftprint, \
            heal_pts, owner, armor, weapon, speed):
        if speed is None:
            raise ValueError('Unit.speed was not specified')
        super().__init__(sess, coords, ftprint, heal_pts, owner, armor, weapon)
        self.speed = speed
        self.dest = self.coords
        self.otype = 'U'



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
