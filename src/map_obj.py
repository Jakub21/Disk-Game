from src.geometry import Point, Vector
from src.footprint import Footprint
from src.weapon import Weapon

class MapObject:
    '''MapObject is an abstract class used for anything placed on board
    Parameters:
        sess [Session] Game session
        coords [Point] Central point of this object's footprint
        ftprint [Footprint] A footprint this object occupies on board
    '''
    def __init__(self, sess, coords, fprint):
        self.session = sess
        self.coords = coords
        self.footprint = fprint
        self.selected = False
        self.tick = 0

    def update(self, tick):
        '''Keeps track of session tick'''
        self.tick = tick

    def get_attrs(self):
        '''Creates dict with data to put in console'''
        return {}

    def check_footprint(self):
        '''Checks if object can be placed at current coordinate'''
        shifted = self.footprint.get_shifted(self.coords.get_vector_orig())
        valid = True
        for pt in shifted.points:
            cell = self.session.board.board[pt.y][pt.x]
            if cell.is_occupied:
                valid = False
                break
            if (self.object_type == 'U') and not cell.crossable:
                valid = False
                break
            elif (self.object_type == 'B') and not cell.buildable:
                valid = False
                break
        return valid

    def apply_footprint(self):
        '''Sets cells' occupied flag to True with itself as occupier object'''
        shifted = self.footprint.get_shifted(self.coords.get_vector_orig())
        for pt in shifted.points:
            self.session.board.board[pt.y][pt.x].occupy(self)

    def remove_footprint(self):
        '''Sets cells' occupied flag to False'''
        shifted = self.footprint.get_shifted(self.coords.get_vector_orig())
        for pt in shifted.points:
            self.session.board.board[pt.y][pt.x].release()

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False



class GameUnit(MapObject):
    '''GameUnit represents objects steerable by player (Buildings and Units)
    Parameters:
        sess [Session] Game session
        heal_pts [int] Amount of heal points this object has
        max_heal_pts [int] Max amount of heal points this object can have
        owner [Player] Owner of this object
        coords [Point] Central point of this object's footprint
        fprint [Footprint] A footprint this object occupies on board
        armor [int] Amount of damage that is substracted every time damage is
            dealt to this object
        weapon [Weapon] weapon used by attack method
    '''
    def __init__(self, sess, coords, fprint, heal_pts, owner, armor, weapon):
        super().__init__(sess, coords, fprint)
        self.heal_pts, self.max_heal_pts = heal_pts, heal_pts
        self.owner = owner
        self.armor = armor
        self.weapon = weapon
        self.can_attack = False
        if not weapon.is_placeholder:
            self.can_attack = True
        self.kill_count = 0
        self.commands = {}
        self.planned = {}

    def update(self, tick):
        '''Updates object state and executes planned actions'''
        super().update(tick)
        self.weapon.update()
        if tick not in self.planned.keys():
            return
        for cmd in self.planned[self.tick]:
            pass # TODO
        del self.planned[self.tick]

    def get_attrs(self):
        '''Creates dict with data to put in console'''
        d = super().get_attrs()
        d.update({
            'heal': '{}/{}'.format(self.heal_pts,self.max_heal_pts),
            'armor': self.armor,
        })
        return d

    def get_heal(self, amount):
        '''Receives healing'''
        heal_pts = self.heal_pts
        heal_pts += amount
        if heal_pts > self.max_heal_pts:
            heal_pts = self.max_heal_pts
        self.heal_pts = heal_pts

    def recv_damage(self, doer):
        '''Receives damage'''
        amount = doer.weapon.damage
        if not doer.weapon.ignore_armor:
            amount -= self.shield
        if amount < -3: amount = 0
        elif amount < 1: amount = 1
        self.heal_pts -= amount
        if self.heal_pts >= 0:
            self.destroy(doer)

    def destroy(self, doer):
        '''Destroys object'''
        self.remove_footprint()
        owner.tell_destroyed(self)
        doer.add_kill_count()
        del self

    def get_hp_frac(self):
        '''Returns fraction of HP'''
        return self.heal_pts / self.max_heal_pts

    def deal_damage(self, target):
        '''Deals damage to the target object'''
        if not self.weapon.is_ready: return
        in_range = self.check_dist(target) <= self.weapon.range
        if in_range:
            target.recv_damage(self)
            return True
        else: return False

    def add_kill(self):
        '''Increments kills count'''
        self.kill_count += 1
        self.owner.kill_count += 1

    def check_dist(self, object):
        '''Check distance to other MapObject'''
        return self.coords.get_vector(object.coords).magnitude



class Building(GameUnit):
    '''Building Class'''
    def __init__(self, sess, coords, fprint, heal_pts, owner, armor, weapon):
        super().__init__(sess, coords, fprint, heal_pts, owner, armor, weapon)
        self.object_type = 'B'



class Unit(GameUnit):
    '''Unit Class'''
    def __init__(self, sess, coords, fprint, heal_pts, owner, armor, weapon,
            speed):
        super().__init__(sess, coords, fprint, heal_pts, owner, armor, weapon)
        self.speed = speed
        self.dest = coords
        self.object_type = 'U'

    def set_dest(self, pos, *args):
        x, y = pos
        self.dest = Point(x, y)

    def stop_all(self, *args):
        super().stop_all()
        self.dest = self.coords


class Resource(MapObject):
    def __init__(self, sess, coords, fprint, rtype, rvalue):
        super().__init__(sess, coords, fprint)
        self.rtype = rtype
        self.rvalue = rvalue
        self.object_type = 'R'

    def get_attrs(self):
        '''Creates dict with data to put in console'''
        d = super().get_attrs()
        d.update({
            'remain': self.rvalue,
        })
        return d
