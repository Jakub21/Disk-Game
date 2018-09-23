'''Create units, buildings and other map-objects usable in-game'''

from src.weapon import Weapon
from src.map_obj import Building, Unit, Resource
from src.footprint import Footprint

################################
# Buildings
################################

class CommandCenter(Building):
    def __init__(self, board, coords, owner):
        fprint = Footprint.rect(27, 27)
        heal_pts = 2000
        armor = 4
        damage, rate, range = 12, 3, 10
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        super().__init__(board, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'command'

class Wall(Building):
    def __init__(self, board, coords, owner):
        fprint = Footprint.rect(11, 11)
        heal_pts = 800
        armor = 2
        weapon = Weapon()
        super().__init__(board, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'wall'

class Tower(Building):
    def __init__(self, board, coords, owner):
        fprint = Footprint.rect(13, 13)
        heal_pts = 1200
        armor = 3
        damage, rate, range = 8, 2, 8
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        super().__init__(board, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'tower'

################################
# Units
################################

class Worker(Unit):
    def __init__(self, board, coords, owner):
        fprint = Footprint.round(3)
        heal_pts = 50
        armor = 0
        damage, rate, range = 1, 2, 2
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        speed = 3
        super().__init__(board,coords,fprint,heal_pts,owner,armor,weapon,speed)
        self.objkey = 'worker'

class Soldier(Unit):
    def __init__(self, board, coords, owner):
        fprint = Footprint.round(5)
        heal_pts = 80
        armor = 0
        damage, rate, range = 6, 2, 2
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        speed = 2
        super().__init__(board,coords,fprint,heal_pts,owner,armor,weapon,speed)
        self.objkey = 'soldier'

################################
# Resources
################################

class WoodField(Resource):
    def __init__(self, board, coords, value):
        fprint = Footprint.round(8)
        super().__init__(board, coords, fprint, 'wood', value)
        self.objkey = 'woodfield'

class IronField(Resource):
    def __init__(self, board, coords, value):
        fprint = Footprint.round(8)
        super().__init__(board, coords, fprint, 'iron', value)
        self.objkey = 'ironfield'

class FuelField(Resource):
    def __init__(self, board, coords, value):
        fprint = Footprint.round(8)
        super().__init__(board, coords, fprint, 'fuel', value)
        self.objkey = 'fuelfield'
