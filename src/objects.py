'''Create units, buildings and other objects'''
from src.geometry import Point
from src.weapon import Weapon
from src.otypes import Building, Unit, Resource, Destructible
from src.footprint import Footprint

################################
# Buildings
################################

class CommandCenter(Building):
    def __init__(self, session, coords, owner):
        fprint = Footprint.square(7)
        heal_pts, armor = 1500, 2
        weapon = Weapon() # Placeholder
        super().__init__(session, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'command'
        self.add_cmd('train_worker', self.session.cmds.train_worker, (0,1))
        self.add_cmd('train_soldier', self.session.cmds.train_soldier, (1,1))

class Wall(Building):
    def __init__(self, session, coords, owner):
        fprint = Footprint.square(2)
        heal_pts, armor = 500, 2
        weapon = Weapon() # Placeholder
        super().__init__(session, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'wall'

class Tower(Building):
    def __init__(self, session, coords, owner):
        fprint = Footprint.square(3)
        heal_pts, armor = 800, 2
        damage, rate, range = 5, 15, 5
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        super().__init__(session, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'tower'

################################
# Units
################################

class Worker(Unit):
    def __init__(self, session, coords, owner):
        fprint = Footprint.round(1.3)
        heal_pts, armor = 50, 0
        damage, rate, range = 5, 10, 2
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        speed = 6
        super().__init__(session,coords,fprint,heal_pts,owner,armor,weapon,speed)
        self.objkey = 'worker'

class Soldier(Unit):
    def __init__(self, session, coords, owner):
        fprint = Footprint.round(1.6)
        heal_pts, armor = 80, 0
        damage, rate, range = 7, 9, 4
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        speed = 4
        super().__init__(session,coords,fprint,heal_pts,owner,armor,weapon,speed)
        self.objkey = 'soldier'

################################
# Resources
################################

class WoodField(Resource):
    def __init__(self, session, coords, value):
        fprint = Footprint.square(2)
        super().__init__(session, coords, fprint, 'wood', value)
        self.objkey = 'woodfield'

class IronField(Resource):
    def __init__(self, session, coords, value):
        fprint = Footprint.square(2)
        super().__init__(session, coords, fprint, 'iron', value)
        self.objkey = 'ironfield'

class FuelField(Resource):
    def __init__(self, session, coords, value):
        fprint = Footprint.square(2)
        super().__init__(session, coords, fprint, 'fuel', value)
        self.objkey = 'fuelfield'

################################
# Destructibles
################################

class SmallRocks(Destructible):
    def __init__(self, session, coords):
        fprint = Footprint.square(4)
        heal_pts, armor = 1000, 1
        super().__init__(session, coords, fprint, heal_pts, armor)
        self.objkey = 'smallrocks'
