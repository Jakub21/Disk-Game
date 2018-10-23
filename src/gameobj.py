
class Object:
    '''Object is an abstract class user for anything placed on board
    Parameters:
        sess [Session] Game session
        coords [Point] Central point of object's footprint
        ftprint [Footprint] A footprint this object occupies on board
    '''
    def __init__(self, sess, coords, ftprint):
        self.session = sess
        self.coords = coords
        self.footprint = ftprint
        self.selected = False
        self.tick = 0

    def update(self, tick):
        '''Keeps track of session's tick'''
        self.tick = tick

    def get_attrs(self):
        '''Creates dict with data to put in console'''
        return {}

    def get_address(self):
        '''Returns a string with objects address (in hex)
        Use to distinguish objects
        '''
        return '<{}'.format(str(self)[-11:])

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False



class Controllable(Object):
    '''Controllable Object represents object controllable by player
    Parameters
        sess [Session] Game session
        coords [Point] Central point of object's footprint
        ftprint [Footprint] A footprint this object occupies on board
        heal_pts [int] Amount of heal points this object has (also max)
        owner [Player] Owner of this object
        armor [int] Amount of damage that is subtracted from hits
        weapon [Weapon] Weapon used by attack method
    '''
    def __init__(self, sess, coords, ftprint, heal_pts, owner, armor, weapon):
        super().__init__(sess, coords, ftprint)
        self.heal_pts, self.max_heal_pts = heal_pts, heal_pts
        self.owner = owner
        self.armor = armor
        self.weapon = weapon

    def update(self, tick):
        '''Updates object state'''
        super().update(tick)
        self.weapon.update()
        # TODO: Commands and Actions

    def get_attrs(self):
        '''Creates dict with data to put in console'''
        d = super().get_attrs()
        d.update({
            'heal': '{}/{}'.format(self.heal_pts,self.max_heal_pts),
            'armor': self.armor,
        })
        return d

    def recv_heal(self, amount):
        '''Receives healing'''
        self.heal_pts += amount
        if self.heal_pts > self.max_heal_pts:
            self.heal_pts = self.max_heal_pts

    def recv_damage(self, doer):
        '''Receives damage'''
        amount = doer.weapon.damage
        if not doer.weapon.ignore_armor:
            amount -= self.armor
        if amount < 0: amount = 0
        self.heal_pts -= amount
        if self.heal_pts <= 0:
            self.destroy(doer)

    def destroy(self, doer):
        '''Destroys object'''
        self.session.tell_destroyed(self)
        if self.owner is not None:
            self.owner.tell_destroyed(self)
        del self

    # TODO: Restore other combat-related methods

    def check_dist(self, object):
        '''Check distance to other MapObject'''
        return Vector.from_point(abs(self.coords-object.coords)).magnitude
