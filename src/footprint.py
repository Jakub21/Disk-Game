from src.geometry import Point, Vector
import numpy as np

import logging
Log = logging.getLogger('MainLogger')

class Footprint:
    '''Footprint Class
    Represents MapObject's footprint on Board, allows custom sizes and shapes
    Listed point are relative to object's center
    '''
    def __init__(self, points=[]):
        '''Creates Footprint from list of points'''
        self.points = points
        self.pt_count = len(points)

    @classmethod
    def round(cls, radius):
        '''Creates round footprint. Recommended for units'''
        obj = cls.__new__(cls)
        pt_count = 0
        points = []
        center = Point(0,0)
        for x in range(-radius, radius+1):
            for y in range(-radius, radius+1):
                current = Point(x, y)
                if center.get_vector(current).magnitude <= radius:
                    points += [current]
                    pt_count += 1
        #
        obj.points = points
        obj.pt_count = pt_count
        return obj

    @classmethod
    def rect(cls, xsize, ysize):
        '''Creates rectangle footprint. Recommended for buildings'''
        if xsize % 2 == 0 or ysize % 2 == 0:
            raise ValueError('Only odd numbers are allowed')
        # TODO: Add support for rectangles of even edge length
        obj = cls.__new__(cls)
        pt_count = 0
        points = []
        center = Point(0,0)
        for x in range(-xsize//2, (xsize//2)):
            for y in range(-ysize//2, (ysize//2)):
                points += [Point(x, y)]
                pt_count += 1
        #
        obj.points = points
        obj.pt_count = pt_count
        return obj

    def get_shifted(self, vector):
        '''Make copy of footprint shifted by some vector'''
        shifted_pts = []
        for pt in self.points:
            pt2 = pt.copy()
            pt2.apply_vector(vector)
            shifted_pts += [pt2]
        return Footprint(shifted_pts)

    def make_array(self):
        '''Creates array with all points'''
        w = min([p.x for p in self.points])
        n = min([p.y for p in self.points])
        pts = self.get_shifted(Vector(-w, -n)).points
        width, height = self.get_width(), self.get_height()
        array = np.zeros((height+1, width+1))
        for pt in pts:
            array[pt.y, pt.x] = 1
        return array

    def getNW(self):
        '''Returns most northward and westward coordinates'''
        w = min([p.x for p in self.points])
        n = min([p.y for p in self.points])
        return Point(-w, -n)

    def get_width(self):
        '''Returns difference between extreme points in X axis'''
        xmin = min([p.x for p in self.points])
        xmax = max([p.x for p in self.points])
        return xmax - xmin

    def get_height(self):
        '''Returns difference between extreme points in Y axis'''
        ymin = min([p.y for p in self.points])
        ymax = max([p.y for p in self.points])
        return ymax - ymin
