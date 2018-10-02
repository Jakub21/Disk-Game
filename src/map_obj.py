from src.geometry import Point, Vector
from src.footprint import Footprint
from src.weapon import Weapon
from src.queue import Queue

import logging
Log = logging.getLogger('MainLogger')

class Command:
    def __init__(self, method, *args ,dur, cost, group, gets_pt, **kwargs):
        self.method = method
        self.args = args
        self.duration = dur
        self.cost = cost
        self.group = group
        self.gets_pt = gets_pt
        self.kwargs = kwargs

    def instance(self, **kwargs):
        kws = self.kwargs.copy()
        kws.update(kwargs)
        return Command(self.method, *self.args, dur=self.duration,
            cost=self.cost, group=self.group, gets_pt=self.gets_pt, **kws)

    def exe(self, object):
        self.method(*self.args, **self.kwargs)



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

    def check_footprint(self, alt=None):
        '''Checks if object can be placed at current coordinate'''
        coords = self.coords if alt is None else alt
        shifted = self.footprint.get_shifted(coords.get_vector_orig())
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
            self.session.board.occupy(pt, self)

    def remove_footprint(self):
        '''Sets cells' occupied flag to False'''
        shifted = self.footprint.get_shifted(self.coords.get_vector_orig())
        for pt in shifted.points:
            self.session.board.release(pt)

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
        self.make_cmd('cancel', self.cancel_all, group=2)

    def update(self, tick):
        '''Updates object state and executes planned actions'''
        super().update(tick)
        self.weapon.update()
        if tick not in self.planned.keys():
            return
        for cmd in self.planned[self.tick]:
            cmd.exe(self)
        try: del self.planned[self.tick]
        except KeyError: pass # canceled

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
        self.session.tell_update_bgr()
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

    def make_cmd(self, key, method, *args, dur=1, cost=(0,0,0), group=0,
        gets_pt=False, **kwargs):
        '''Adds action triggerable by player
        Parameters
            key [str] Command key
            method [func] Method to execute
            dur [int](1) Action delay (duration) in ticks
            cost [3-int](0,0,0) Action cost
            group [int](0) If is 0 action in executed on single object. If is 1,
                action is executed on objects of type same as 1st in selection
                If 2, action is executed on every object in selection.
            gets_pt [bool](False) If True, user must L-click board first
                to point coords of target. Coords are passed under "pos" kw.
            *args and **kwargs are passed to method
        '''
        cmd = Command(method, *args, dur=dur, cost=cost, group=group,
            gets_pt=gets_pt, **kwargs)
        self.commands[key] = cmd

    def queue_cmd(self, key, **kwargs):
        '''Adds action to "planned" queue'''
        tick = self.tick
        try: duration = self.commands[key].duration
        except KeyError: return # Commands for units groups
        instance = self.commands[key].instance(**kwargs)
        try: self.planned[tick+duration] += [instance]
        except KeyError: self.planned[tick+duration] = [instance]

    # Commands

    def cancel_all(self):
        for action_lists in self.planned.values():
            for action in action_lists:
                self.owner.giveback(action.cost) # TODO
        self.planned = {}

    def train_unit(self, target_cls, *args):
        unit = target_cls(self.session, self.coords, self.owner)
        unit.coords = self.coords.copy()
        delta = self.footprint.get_height()//2 + unit.footprint.get_height()//2
        unit.coords.apply_vector(Vector(0, delta))
        unit.dest = unit.coords.copy()
        self.session.add_object(unit)



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
        self.dest = [coords]
        self.object_type = 'U'
        self.path_pts = Queue()
        self.make_cmd('cancel', self.cancel_all, group=2)
        self.make_cmd('move', self.set_dest, gets_pt=True, group=2)

    def update(self, tick):
        '''Updates object state'''
        super().update(tick)
        # Move
        dest = self.dest.get()
        if self.coords.get() != dest:
            self.session.tell_update_bgr()
        total_cost = 0
        self.remove_footprint()
        while self.coords.get() != dest and total_cost < self.speed:
            prev = self.coords.copy()
            self.coords = Point(*self.path_pts.pop())
            if not self.check_footprint():
                self.path_pts.add(self.coords.get(),-1)
                self.coords = prev
                break
            cost = 1
            if self.coords.x != prev.x and self.coords.y != prev.y:
                cost = 1.7 # Diagonal (sqrt(2) caused units to be too fast)
            total_cost += cost
        self.apply_footprint()

    def set_dest(self, pos, *args):
        self.dest = Point(*pos)
        fp = self.footprint.make_array()
        new_dest, pts = self.session.board.find(fp, self.coords, self.dest)
        self.dest = Point(*new_dest) # Dest is updated when old was at obstacle
        self.path_pts.set_empty()
        self.path_pts.add_many(pts)

    #def add_dest(self, pos, *args):
    #    dest = Point(*pos)
    #    coords, dest = self.coords.get(), self.dest.get()
    #    self.path_pts.add_many(self.session.board.find(dest, self.dest))
    #    self.dest = dest

    def cancel_all(self, *args):
        super().cancel_all()
        self.dest = self.coords
        self.path_pts.set_empty()



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
