'''Create units, buildings and other map-objects usable in-game'''
from src.geometry import Point
from src.weapon import Weapon
from src.map_obj import Command, Building, Unit, Resource
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
        self.commands['train_worker'] = Command(self.train_unit, Worker,
            cost=(50,0,0))
        self.commands['train_soldier'] = Command(self.train_unit, Soldier,
            cost=(100,50,0))
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
        speed = 1.7
        super().__init__(board,coords,fprint,heal_pts,owner,armor,weapon,speed)
        self.commands['build_wall'] = Command(self.build, Wall,
            cost=(200,0,0), gets_pt=True)
        self.commands['build_tower'] = Command(self.build, Tower,
            cost=(250,100,0), gets_pt=True)
        self.objkey = 'worker'

    def build(self, target_cls, pos, *args):
        coords = Point(*pos)
        building = target_cls(self.session, coords, self.owner)
        self.session.add_object(building)

class Soldier(Unit):
    def __init__(self, board, coords, owner):
        fprint = Footprint.round(5)
        heal_pts = 80
        armor = 0
        damage, rate, range = 6, 2, 2
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
