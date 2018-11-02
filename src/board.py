from numpy import array
from random import randrange as rand
from PIL import Image
from src.geometry import Point, Vector

import logging
Log = logging.getLogger('MainLogger')

class Cell:
    '''Class represents board cell'''
    def __init__(self, coords, crossable, size, var_count):
        self.coords = coords
        self.crossable = crossable
        self.size = size
        self.occupied = 0
        self.sqr_occupier = None
        self.subcells = [[None for x in range(size)] for y in range(size)]
        self.variant = 'free' if self.crossable else 'obst'
        self.variant += str(rand(0, var_count))
        self.orig_variant = self.variant # When occupied, variant is changed

    def get_object(self, subcoords):
        if self.sqr_occupier is not None:
            return self.sqr_occupier
        x, y = subcoords
        xx, yy = int(x*self.size), int(y*self.size)
        return self.subcells[yy][xx]

    def occupy(self, obj):
        if not self.crossable: return False
        if obj.footprint.is_square:
            if self.occupied != 0: return False
            self.occupied = 2
            self.sqr_occupier = obj
            return True
        else:
            return self.sub_occupy(obj)

    def sub_occupy(self, obj):
        if not self.crossable: return False
        if self.occupied == 2: return False
        size = obj.footprint.size / 2 # Radius
        for x in range(self.size):
            for y in range(self.size):
                sx, sy = self.coords.get()
                coords = Point(sx+(x/self.size), sy+(y/self.size))
                v = Vector.from_abs(obj.coords, coords)
                if v.magnitude > size:
                    continue
                if self.subcells[y][x] is not None:
                    return False
                self.subcells[y][x] = obj
        self.occupied = 1
        return True

    def release(self, obj):
        if obj.footprint.is_square:
            if self.sqr_occupier is not obj:
                return
            self.occupied = 0
            self.sqr_occupier = None
        else:
            return self.sub_release(obj)

    def sub_release(self, obj):
        size = self.size
        rad = obj.footprint.size
        delta = obj.coords - self.coords
        for x in range(size):
            for y in range(size):
                if self.subcells[y][x] == obj:
                    self.subcells[y][x] = None
        ncnt = sum(1 for row in self.subcells for e in row if e is None)
        self.occupied = 0 if ncnt == pow(size, 2) else 1



class Board:
    def __init__(self, session, path):
        Log.debug('Creating board')
        self.variant = 'grassland' # TODO
        self.session = session
        self.CORE = session.app.CORE
        self.CLRS = session.app.CLRS
        self.starts = []
        self.toplace = []
        self.load_png(path)

    def get(self, coords):
        try: x, y = coords.get() # Point obj
        except: x, y = coords # Point (tuple)
        return self.cells[int(y)][int(x)]

    def get_object(self, coords):
        try: x, y = coords.get() # Point obj
        except: x, y = coords # Point (tuple)
        sx, sy = round((x%1), 3), round((y%1), 3)
        subs = self.CORE.sub_per_cell
        cell = self.cells[int(y)][int(x)]
        return cell.get_object((x%1,y%1))

    def apply_fp(self, obj):
        fp = obj.footprint
        success = True
        if fp.is_square:
            vector = Vector.from_point(obj.coords)
            for pt in fp.points:
                pt = pt + vector
                if not self.get(pt).occupy(obj):
                    success = False
            if not success:
                self.release_fp(obj)
                return False
        else:
            cx, cy = obj.coords.get()
            radius = fp.size / 2
            gr = radius / self.CORE.sub_per_cell
            for y in range(int(cy-gr/2)-1, int(cy+gr/2)+2):
                if not success: break
                for x in range(int(cx-gr/2)-1, int(cx+gr/2)+2):
                    if not self.get((x,y)).occupy(obj):
                        success = False
                        break
            if not success:
                self.release_fp(obj)
                return False
        return True

    def release_fp(self, obj):
        fp = obj.footprint
        if fp.is_square:
            vector = Vector.from_point(obj.coords)
            for pt in fp.points:
                pt = pt + vector
                self.get(pt).release(obj)
        else:
            cx, cy = obj.coords.get()
            radius = fp.size / 2
            gr = radius / self.CORE.sub_per_cell
            for y in range(int(cy-gr/2)-1, int(cy+gr/2)+2):
                for x in range(int(cx-gr/2)-1, int(cx+gr/2)+2):
                    self.get((x,y)).release(obj)

    def get_cell_gfx(self, coords):
        try: x, y = coords.get() # Point obj
        except: x, y = coords # Point (tuple)
        return self.cgroups[y][x].variant

    def load_png(self, filename):
        defines = {k:tuple(v) for k,v in self.CLRS.board_file_defines.items()}
        pillow = Image.open(filename)
        self.size = pillow.size
        width, height = pillow.size
        pixels = pillow.load()
        self.cells = [[None for x in range(width)] for y in range(height)]
        var_count = self.CORE.variant_count
        sub_per_cell = self.CORE.sub_per_cell
        for y in range(height):
            for x in range(width):
                point = Point(x, y)
                try: key = self.find_key(defines, pixels[x, y])
                except KeyError:
                    Log.info('Invalid color {} in map "{}"' + \
                        ' at position {}'.format( pixels[x, y],
                        path.split('/')[-1], (x,y)))
                    raise
                if key == 'start_pos': self.starts += [point]
                elif 'norm' in key or 'rich' in key:
                    self.toplace+=[(point, key)]
                crossable = key != 'not_crsbl'
                cell = Cell(point, crossable, sub_per_cell, var_count)
                self.cells[y][x] = cell

    @staticmethod
    def find_key(dict, value):
        for k, v in dict.items():
            if v == value:
                return k
        raise KeyError('Could not find key of this value: {}'.format(value))
