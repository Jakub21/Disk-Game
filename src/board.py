from src.geometry import Point
from PIL import Image
import numpy as np
import src.jps as jps

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
        self.is_occupied = 0
        self.object = None
        if not crossable:
            buildable = False
        self.crossable = crossable
        self.buildable = buildable
        self.coords = coords

    def _occupy(self, object):
        '''Adds cell occupier (map-object)
        If object is an unit, is_occupied attr is set to 1, else to 2
        '''
        self.is_occupied = 1 if object.object_type == 'U' else 2
        self.object = object

    def _release(self):
        '''Removes cell occupier (map-object)'''
        self.is_occupied = 0
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
        self.init_finder_field()
        self.finder = jps.Finder(self)

    def init_finder_field(self):
        width, height = self.size
        self.finder_field = np.array([[0 if self.board[y][x].crossable and
            self.board[y][x].is_occupied < 2 else -1 for x in range(width)]
            for y in range(height)])

    def occupy(self, coords, object):
        x, y = coords.get()
        self.board[y][x]._occupy(object)
        if object.object_type != 'U':
            self.finder_field[y, x] = -1

    def release(self, coords):
        x, y = coords.get()
        object = self.board[y][x].object
        self.board[y][x]._release()
        if object.object_type != 'U':
            self.finder_field[y][x] = 0

    def find(self, fp, orig, dest):
        return self.finder.find(self.finder_field, self.size, fp, orig, dest)

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
