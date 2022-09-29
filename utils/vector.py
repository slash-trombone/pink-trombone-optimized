import math
import random
import sys


def _approx_eq(a, b, tol=sys.float_info.epsilon):
        return abs(a-b) <= max(abs(a), abs(b))/2. * tol


class Vector2:
    def __init__(self, x=0., y=0.):
        self._x = x
        self._y = y
        self._length_dirty = True
        self._length_sq_dirty = True
        self._normal_dirty = True
        self._length = None
        self._length_sq = None
        self._normal = None

    def __iter__(self):
        yield self._x
        yield self._y

    def __repr__(self):
        return "[{0}, {1}]".format(self._x, self._y)

    def __str__(self):
        return "[{0:.3f}, {1:.3f}]".format(self._x, self._y)

    def __getitem__(self, index):
        if index == 0 or index == 'x':
            return self._x
        elif index == 1 or index == 'y':
            return self._y
        raise IndexError()

    def __add__(self, other):
        return Vector2(self._x + other._x,
                       self._y + other._y)

    def __sub__(self, other):
        return Vector2(self._x - other._x,
                       self._y - other._y)

    def __mul__(self, s):
        if isinstance(s, Vector2):
            return (self._x * s._x) + (self._y * s._y)
        else:
            return Vector2(self._x * s, self._y * s)

    def __eq__(self, other):
        return (_approx_eq(self.x, other.x) and
                _approx_eq(self.y, other.y))

    def _makeDirty(self):
        self._length_dirty = True
        self._length_sq_dirty = True
        self._normal_dirty = True

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._makeDirty()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._makeDirty()

    @property
    def normal(self):
        if self._normal_dirty:
            l = self.length
            if _approx_eq(l, 0.):
                self._normal = Vector2.Zero()
            else:
                self._normal = self * (1. / l)
            self._normal_dirty = False
        return self._normal

    @property
    def length(self):
        if self._length_dirty:
            self._length = math.sqrt(self.x * self.x + self.y * self.y)
            self._length_dirty = False
        return self._length

    @property
    def length_sq(self):
        if self._length_sq_dirty:
            self._length_sq = self.x * self.x + self.y * self.y
            self._length_sq_dirty = False
        return self._length_sq

    def Normalize(self):
        l = self.length
        if _approx_eq(l, 0.):
            self._x = self._y = 0.
        else:
            self._x = self._x / l
            self._y = self._y / l
        self._makeDirty()

    @staticmethod
    def Right():
        return Vector2(1., 0.)

    @staticmethod
    def Up():
        return Vector2(0., 1.)

    @staticmethod
    def Left():
        return Vector2(-1., 0.)

    @staticmethod
    def Down():
        return Vector2(0., -1.)

    @staticmethod
    def Zero():
        return Vector2(0., 0.)

    @staticmethod
    def One():
        return Vector2(1., 1.)

    @staticmethod
    def Random(x=None, y=None):
        if x is None:
            x = random.random()
        if y is None:
            y = random.random()
        return Vector2Normal(Vector2(x, y))


def Vector2Add(a, b):
    return Vector2(a._x + b._x, a._y + b._y)


def Vector2Sub(a, b):
    return Vector2(a._x - b._x, a._y - b._y)


def Vector2Dot(a, b):
    return (a._x * b._x) + (a._y * b._y)


def Vector2Scale(v, s):
    return Vector2(v._x * s, v._y * s)


def Vector2Length(v):
    return math.sqrt(v.x * v.x + v.y * v.y)


def Vector2LengthSq(v):
    return Vector2Dot(v, v)


def Vector2Normal(v):
    l = Vector2Length(v)
    if _approx_eq(l, 0.):
        return Vector2.Zero()
    return Vector2(v._x / l, v._y / l)


class Vector3(Vector2):
    def __init__(self, x=0., y=0., z=0.):
        self._z = z
        super().__init__(x, y)

    def __iter__(self):
        super().__iter__()
        yield self._z

    def __repr__(self):
        return "[{0}, {1}, {2}]".format(self._x, self._y, self._z)

    def __str__(self):
        return "[{0:.3f}, {1:.3f}, {2:.3f}]".format(self._x, self._y, self._z)

    def __getitem__(self, index):
        if index == 0 or index == 'x' or index == 'r':
            return self._x
        elif index == 1 or index == 'y' or index == 'g':
            return self._y
        elif index == 2 or index == 'z' or index == 'b':
            return self._z
        raise IndexError()

    def __add__(self, other):
        return Vector3(self._x + other._x,
                       self._y + other._y,
                       self._z + other._z)

    def __sub__(self, other):
        return Vector3(self._x - other._x,
                       self._y - other._y,
                       self._z - other._z)

    def __mul__(self, s):
        if isinstance(s, Vector3):
            return (self._x * s._x) + (self._y * s._y) + (self._z * s._z)
        else:
            return Vector3(self._x * s, self._y * s, self._z * s)

    def __eq__(self, other):
        return (_approx_eq(self.x, other.x) and
                _approx_eq(self.y, other.y) and
                _approx_eq(self.z, other.z))

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value
        self._makeDirty()

    @property
    def r(self):
        return self._x

    @r.setter
    def r(self, r):
        self._x = r
        self._makeDirty()

    @property
    def g(self):
        return self._y

    @g.setter
    def g(self, g):
        self._y = g
        self._makeDirty()

    @property
    def b(self):
        return self._z

    @b.setter
    def b(self, z):
        self._z = z
        self._makeDirty()

    @property
    def normal(self):
        if self._normal_dirty:
            l = self.length
            if _approx_eq(l, 0.):
                self._normal = Vector3.Zero()
            else:
                self._normal = self * (1 / l)
            self._normal_dirty = False
        return self._normal

    @property
    def length(self):
        if self._length_dirty:
            self._length = math.sqrt(self * self)
            self._length_dirty = False
        return self._length

    @property
    def length_sq(self):
        if self._length_sq_dirty:
            self._length_sq = self * self
            self._length_sq_dirty = False
        return self._length_sq

    def Normalize(self):
        l = self.length
        if _approx_eq(l, 0.):
            self._x = self._y = self._z = 0.
        else:
            self._x = self._x / l
            self._y = self._y / l
            self._z = self._z / l
        self._makeDirty()

    @staticmethod
    def Random(x=None, y=None, z=None):
        if x is None:
            x = random.random()
        if y is None:
            y = random.random()
        if z is None:
            z = random.random()
        return Vector3Normal(Vector3(x, y, z))

    @staticmethod
    def Right():
        return Vector3(1., 0., 0.)

    @staticmethod
    def Up():
        return Vector3(0., 1., 0.)

    @staticmethod
    def Backward():
        return Vector3(0., 0., 1.)

    @staticmethod
    def Left():
        return Vector3(-1., 0., 0.)

    @staticmethod
    def Down():
        return Vector3(0., -1., 0.)

    @staticmethod
    def Forward():
        return Vector3(0., 0., -1.)

    @staticmethod
    def Zero():
        return Vector3(0., 0., 0.)

    @staticmethod
    def One():
        return Vector3(1., 1., 1.)


def Vector3Add(a, b):
    return Vector3(a._x + b._x, a._y + b._y, a._z + b._z)


def Vector3Sub(a, b):
    return Vector3(a._x - b._x, a._y - b._y, a._z - b._z)


def Vector3Dot(a, b):
    return (a._x * b._x) + (a._y * b._y) + (a._z * b._z)


def Vector3Scale(v, s):
    return Vector3(v._x * s, v._y * s, v._z * s)


def Vector3Length(v):
    return math.sqrt(Vector3Dot(v, v))


def Vector3LengthSq(v):
    return Vector3Dot(v, v)


def Vector3Normal(v):
    l = Vector3Length(v)
    if _approx_eq(l, 0.):
        return Vector3.Zero()
    return Vector3(v._x / l, v._y / l, v._z / l)