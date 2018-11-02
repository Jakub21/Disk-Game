from math import sqrt, atan, pi, sin, cos

class Base:
    '''Magic methods shared by Point and Vector classes'''
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __imul__(self, other):
        self.x = self.x*other
        self.y = self.y*other

    def __idiv__(self, other):
        self.x /= other
        self.y /= other

    def __ifloordiv__(self, other):
        self.x //= other
        self.y //= other

    def __imod__(self, other):
        self.x %= other
        self.y %= other

    def __neg__(self):
        self.x = -self.x
        self.y = -self.y

    def __abs__(self):
        self.x = abs(self.x)
        self.y = abs(self.y)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)



class Point(Base):
    '''Point with X and Y coordinates'''
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def __add__(self, other):
        x, y = self.x+other.x, self.y+other.y
        return Point(x,y)

    def __sub__(self, other):
        x, y = self.x-other.x, self.y-other.y
        return Point(x,y)

    def __mul__(self, other):
        x, y = self.x*other, self.y*other
        return Point(x,y)

    def __div__(self, other):
        x, y = self.x/other, self.y/other
        return Point(x,y)

    def __floordiv__(self, other):
        x, y = self.x//other, self.y//other
        return Point(x,y)

    def __mod__(self, other):
        x, y = self.x%other, self.y%other
        return Point(x,y)

    def copy(self):
        '''Create a copy of this Point'''
        return Point(self.x, self.y)

    def get(self):
        '''Returns 2-tuple with coordinates'''
        return self.x, self.y

    def to_ints(self):
        self.x = int(self.x)
        self.y = int(self.y)

    def round(self, positions):
        '''Rounds coordinates'''
        self.x = round(self.x, positions)
        self.y = round(self.y, positions)



class Vector(Base):
    '''Class represents 2D Euclidean Vector.
    Contains method for method usable on plane'''
    def __init__(self, x=0, y=0):
        '''Create a Vector, basing on its deltas'''
        self.x, self.y = x, y
        self.recalc()

    @classmethod
    def from_rotation(cls, rotation, magnitude):
        '''Create vector, basing on its rotation and magnitude'''
        obj = cls.__new__(cls)
        xratio = cos(cls.to_rads(rotation))
        yratio = sin(cls.to_rads(rotation))
        obj.x = xratio * magnitude
        obj.y = yratio * magnitude
        obj.recalc()
        return obj

    @classmethod
    def from_abs(cls, init_pt, term_pt):
        '''Create a vector, basing on coords of its init and term points'''
        obj = cls.__new__(cls)
        obj.x = init_pt.x - term_pt.x
        obj.y = init_pt.y - term_pt.y
        obj.recalc()
        return obj

    @classmethod
    def from_point(cls, point):
        '''Create vector from Point (init at origin, term at point)'''
        obj = cls.__new__(cls)
        obj.x = point.x
        obj.y = point.y
        obj.recalc()
        return obj

    def __repr__(self):
        '''Generate repr string of the Vector'''
        return 'Vector [{}, {}]'.format(self.x, self.y)

    def __add__(self, other):
        x, y = self.x+other.x, self.y+other.y
        return Vector(x,y)

    def __sub__(self, other):
        x, y = self.x-other.x, self.y-other.y
        return Vector(x,y)

    def __mul__(self, other):
        x, y = self.x*other, self.y*other
        return Vector(x,y)

    def __div__(self, other):
        x, y = self.x/other, self.y/other
        return Vector(x,y)

    def __floordiv__(self, other):
        x, y = self.x//other, self.y//other
        return Vector(x,y)

    def __mod__(self, other):
        x, y = self.x%other, self.y%other
        return Vector(x,y)

    def copy(self):
        '''Create a copy of this Vector'''
        return Vector(self.x, self.y)

    def recalc(self):
        '''Recalculate magnitude and angle of the Vector'''
        self.magnitude = sqrt(self.x**2 + self.y**2)
        try: angle = atan(self.y/self.x)
        except ZeroDivisionError:
            angle = 180 if self.x < 0 else 0
        angle = round(self.to_degs(angle), 2)
        if self.x < 0: angle = 180+angle # diff but angle is negative
        if self.x > 0 and self.y < 0:
            angle = 360+angle # diff but angle is negative
        if self.x == 0:
            angle = (90 if self.y > 0 else 270) if self.y != 0 else 0
        self.angle = angle

    def get(self):
        return self.x, self.y

    def scale(self, scalar):
        '''Scale vector by some value'''
        self.x = self.x*scalar
        self.y = self.y*scalar
        self.recalc()

    def add(self, vector):
        '''Sum with another vector'''
        self.x += vector.x
        self.y += vector.y
        self.recalc()

    def transform(self, matrice):
        '''Perform transformation (2x2 matrice)'''
        xx, xy = matrice[0]
        yx, yy = matrice[1]
        new_x = xx*self.x, xy*self.y
        new_y = yx*self.x, yy*self.y
        self.x = new_x[0] + new_y[0]
        self.y = new_x[1] + new_y[1]
        self.recalc()

    @staticmethod
    def to_rads(degs):
        return (degs*2*pi)/360

    @staticmethod
    def to_degs(rads):
        return (rads*360)/(2*pi)
