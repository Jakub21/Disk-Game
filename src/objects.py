'''Create units, buildings and other objects'''
from src.geometry import Point
from src.weapon import Weapon
from src.otypes import Building, Unit, Resource
from src.footprint import Footprint

################################
# Buildings
################################

class CommandCenter(Building):
    def __init__(self, board, coords, owner):
        fprint = Footprint.square(7)
        heal_pts = 2000
        armor = 2
        damage, rate, range = 40, 60, 8
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        super().__init__(board, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'command'

class Wall(Building):
    def __init__(self, board, coords, owner):
        fprint = Footprint.square(2)
        heal_pts = 800
        armor = 2
        weapon = Weapon() # Placeholder
        super().__init__(board, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'wall'

class Tower(Building):
    def __init__(self, board, coords, owner):
        fprint = Footprint.square(3)
        heal_pts = 1000
        armor = 2
        damage, rate, range = 15, 30, 5
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        super().__init__(board, coords, fprint, heal_pts, owner, armor, weapon)
        self.objkey = 'tower'

################################
# Units
################################

class Worker(Unit):
    def __init__(self, board, coords, owner):
        fprint = Footprint.round(1.3)
        heal_pts = 50
        armor = 0
        damage, rate, range = 5, 20, 2
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        speed = 1.7
        super().__init__(board,coords,fprint,heal_pts,owner,armor,weapon,speed)
        self.objkey = 'worker'

class Soldier(Unit):
    def __init__(self, board, coords, owner):
        fprint = Footprint.round(1.6)
        heal_pts = 80
        armor = 0
        damage, rate, range = 7, 17, 4
        ignore_armor = False
        weapon = Weapon(damage, rate, range, ignore_armor)
        speed = 1.4
        super().__init__(board,coords,fprint,heal_pts,owner,armor,weapon,speed)
        self.objkey = 'soldier'

################################
# Resources
################################

class WoodField(Resource):
    def __init__(self, board, coords, value):
        fprint = Footprint.square(2)
        super().__init__(board, coords, fprint, 'wood', value)
        self.objkey = 'woodfield'

class IronField(Resource):
    def __init__(self, board, coords, value):
        fprint = Footprint.square(2)
        super().__init__(board, coords, fprint, 'iron', value)
        self.objkey = 'ironfield'

class FuelField(Resource):
    def __init__(self, board, coords, value):
        fprint = Footprint.square(2)
        super().__init__(board, coords, fprint, 'fuel', value)
        self.objkey = 'fuelfield'
