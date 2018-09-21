from src.geometry import Point
from PIL import Image

import logging
Log = logging.getLogger('MainLogger')

class BoardCell:
    '''Board Cell
    Init Parameters:
        coords [Point] location on board
        crossable [bool](True) specifies if units can move here
        buildable [bool](True) specifies if buildings can be built here
    Note that if cell's crossable flag is False, buildable flag is automatically
        set to False
    '''
    def __init__(self, coords, crossable=True, buildable=True):
        self.is_occupied = False
        self.object = None
        if not crossable:
            buildable = False
        self.crossable = crossable
        self.buildable = buildable
        self.coords = coords

    def occupy(self, object):
        '''Add cell occupier (map-object)'''
        self.is_occupied = True
        self.object = object

    def release(self):
        '''Remove cell occupier (map-object)'''
        self.is_occupied = False
        self.object = None



class Board:
    def __init__(self, session, path):
        '''Loads Board data from map file'''
        self.session = session
        self.CLRS = self.session.app_inst.CLRS
        self.CORE = self.session.app_inst.CORE
        self.starting_positions = []
        self.objects_toplace = []
        self.load(path)

    def load(self, path):
        Log.debug('Loading map from file')
        defines = {k:tuple(v) for k,v in self.CLRS.map_src.items()}
        pillow = Image.open(path)
        self.size = pillow.size
        width, height = self.size
        pixels = pillow.load()
        self.board = [[None for x in range(width)] for y in range(height)]
        for y in range(height):
            for x in range(width):
                pt = Point(x,y)
                is_crossable, is_buildable = True, True
                try: key = self.find_key(defines, pixels[y, x])
                except KeyError:
                    Log.info('Invalid color {} in map "{}"' + \
                        ' at position {}'.format( pixels[y, x],
                        path.split('/')[-1], (x,y)))
                    raise
                if key == 'start_pos': self.starting_positions += [pt]
                elif key == 'nowalking': is_crossable = False
                elif key == 'no_builds': is_buildable = False
                elif 'norm' in key or 'rich' in key:
                    self.objects_toplace+=[(pt, key)]
                cell = BoardCell(pt, is_crossable, is_buildable)
                self.board[y][x] = cell

    def gen_background(self):
        Log.debug('Generating background')
        fct = self.CORE.cell_size
        width, height = self.size
        pillow = Image.new('RGB', (width, height))
        pixels = pillow.load()
        colors = self.CLRS.background
        for y in range(height):
            for x in range(width):
                cell = self.board[y][x]
                if cell.crossable and cell.buildable:
                    color = colors[0]
                else:
                    if cell.crossable: color = colors[1]
                    else: color = colors[2]
                pixels[y, x] = tuple(color)
        pillow = pillow.resize((width*fct, height*fct))
        return pillow

    def gen_minimap(self, size):
        Log.debug('Generating mini-map background')
        maxw, maxh = size
        width, height = self.size
        scale = min(maxw/width, maxh/height)
        pillow = Image.new('RGB', self.size)
        pixels = pillow.load()
        colors = self.CLRS.background
        for y in range(height):
            for x in range(width):
                cell = self.board[y][x]
                if cell.crossable and cell.buildable:
                    color = colors[0]
                else:
                    if cell.crossable: color = colors[1]
                    else: color = colors[2]
                pixels[y, x] = tuple(color)
        pillow = pillow.resize((int(width*scale), int(height*scale)))
        Log.debug('MM bgr size: '+str(pillow.size))
        return pillow

    @staticmethod
    def find_key(dict, value):
        for k, v in dict.items():
            if v == value:
                return k
        raise KeyError('Could not find key of this value: {}'.format(value))
