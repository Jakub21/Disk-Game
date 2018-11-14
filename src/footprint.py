from src.geometry import Point
from numpy import zeros
from math import sqrt, ceil

class Footprint:
    '''Footprint class defines area an object occupies on board
    Round FPs should be used for moving units
    Square FPs should be used for buildings, resources, destructibles etc
    '''
    @classmethod
    def square(cls, size):
        '''Creates square FP. size [int] square side length'''
        obj = cls.__new__(cls)
        obj.size = size
        points = []
        center = Point(0,0)
        for x in range(-size//2, (size//2)):
            for y in range(-size//2, (size//2)):
                points += [Point(x+1, y+1)]
        obj.points = points
        obj.is_square = True
        return obj

    @classmethod
    def round(cls, size):
        '''Creates round FP. size [float] circle diameter'''
        obj = cls.__new__(cls)
        obj.size = size
        obj.is_square = False
        return obj

    def get_morph_kernel(self):
        size = ceil(self.size)
        a = zeros((size, size))
        center = self.size//2
        for x in range(size):
            for y in range(size):
                delta = sqrt(abs(x-center)**2 + abs(y-center)**2)
                if delta <= ceil(self.size/2):
                    a[y, x] = 1
        return a
