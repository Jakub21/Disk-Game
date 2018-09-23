from math import sqrt, atan, pi, sin, cos

class Point:
    '''Point with X and Y coordinates'''
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return 'Point('+str(self.x)+', '+str(self.y)+')'

    def copy(self):
        '''Create a copy of this Point'''
        return Point(self.x, self.y)

    def round(self, amount):
        '''Rounds coordinates to be multiples of amount'''
        self.x = self.x-self.x%amount
        self.y = self.y-self.y%amount

    def apply_vector(self, vector):
        '''Shift point by some vector'''
        self.x += vector.xdelta
        self.y += vector.ydelta

    def subtract_vector(self, vector):
        '''Shift point by inversion of some vector'''
        self.x -= vector.xdelta
        self.y -= vector.ydelta

    def get_vector(self, other):
        '''Returns vector between SELF and OTHER'''
        return Vector.from_abs(self, other)

    def get_vector2(self, other):
        '''Returns vector between OTHER and SELF'''
        return Vector.from_abs(other, self)

    def get_vector_orig(self):
        '''Returns vector between origin SELF and the Origin (Point(0,0))'''
        return Vector.from_abs(self, Point(0,0))

    def get(self):
        '''Returns 2-tuple with coordinates'''
        return self.x, self.y



class Vector:
    '''Class represents Euclidean Vector.
    Contains method for method usable on plane'''
    def __init__(self, xdelta=0, ydelta=0):
        '''Create a Vector, basing on its deltas'''
        self.xdelta, self.ydelta = xdelta, ydelta
        self.recalc()

    @classmethod
    def from_rotation(cls, rotation, magnitude):
        '''Create vector, basing on its rotation and magnitude'''
        obj = cls.__new__(cls)
        xratio = cos(cls.to_rads(rotation))
        yratio = sin(cls.to_rads(rotation))
        obj.xdelta = xratio * magnitude
        obj.ydelta = yratio * magnitude
        obj.recalc()
        return obj

    @classmethod
    def from_abs(cls, init_pt, term_pt):
        '''Create a vector, basing on coords of its init and term points'''
        obj = cls.__new__(cls)
        obj.xdelta = init_pt.x - term_pt.x
        obj.ydelta = init_pt.y - term_pt.y
        obj.recalc()
        return obj

    @classmethod
    def from_sum(cls, vectors):
        '''Create vector by summing vectors from the list'''
        obj = cls.__new__(cls)
        obj.xdelta = sum([v.xdelta for v in vectors])
        obj.ydelta = sum([v.ydelta for v in vectors])
        obj.recalc()
        return obj

    def __repr__(self):
        '''Generate repr string of the Vector'''
        return 'Vector '+str([self.xdelta, self.ydelta])

    def copy(self):
        '''Create a copy of this Vector'''
        return Vector(self.xdelta, self.ydelta)

    def recalc(self):
        '''Recalculate magnitude and angle of the Vector'''
        self.magnitude = sqrt(self.xdelta**2 + self.ydelta**2)
        if self.xdelta != 0:
            try: slope = self.xdelta / self.ydelta
            except ZeroDivisionError:
                if self.xdelta < 0: slope = float('inf')
                elif self.xdelta > 0: slope = -float('inf')
                else: slope = 0
            degs = 360*atan(slope)/2*pi
            if self.xdelta < 0 and self.ydelta > 0: degs = 180 - abs(degs)
            if self.xdelta > 0 and self.ydelta > 0: degs = 180 + abs(degs)
            if self.xdelta == 0 and self.ydelta > 0: degs += 180
            degs += 90
            if self.xdelta == 0 and self.ydelta == 0: degs = 0
            self.angle = degs
        else: self.angle = 0

    def get(self):
        return self.xdelta, self.ydelta

    def round(self, positions=0):
        '''Round vector's values to intigers or $ positions after comma'''
        if positions == 0:
            self.xdelta = int(self.xdelta)
            self.ydelta = int(self.ydelta)
        else:
            self.xdelta = round(self.xdelta, positions)
            self.ydelta = round(self.ydelta, positions)
        self.recalc()

    def scale(self, scalar):
        '''Scale vector by some value'''
        self.xdelta = self.xdelta*scalar
        self.ydelta = self.ydelta*scalar
        self.recalc()

    def add(self, vector):
        '''Sum with another vector'''
        self.xdelta += vector.xdelta
        self.ydelta += vector.ydelta
        self.recalc()

    def transform(self, matrice):
        '''Perform transformation (2x2 matrice)'''
        xx, xy = matrice[0]
        yx, yy = matrice[1]
        new_x = xx*self.xdelta, xy*self.ydelta
        new_y = yx*self.xdelta, yy*self.ydelta
        self.xdelta = new_x[0] + new_y[0]
        self.ydelta = new_x[1] + new_y[1]
        self.recalc()

    @staticmethod
    def to_rads(degs):
        return (degs*2*pi)/360
