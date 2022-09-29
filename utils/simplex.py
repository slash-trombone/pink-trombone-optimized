from utils.vector import Vector3
from math import sqrt
import random


class Grad(Vector3):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def dot(self, x, y):
        return self.x*x + self.y*y


def fisher_yates_shuffle(items):
    item_len = len(items)
    for i in range(item_len):
        randomIndex = random.randint(i, item_len-1)
        items[randomIndex], items[i] = items[i], items[randomIndex]
    return items


class Simplex2D:
    _F2 = 0.5 * (sqrt(3.) - 1.)
    _G2 = (3. - sqrt(3.)) / 6.

    _grad3 = (Grad(1., 1., 0.),   Grad(-1., 1., 0.),  Grad(1., -1., 0.),
              Grad(-1., -1., 0.), Grad(1., 0., 1.),   Grad(-1., 0., 1.),
              Grad(1., 0., -1.),  Grad(-1., 0., -1.), Grad(0., 1., 1.),
              Grad(0., -1., 1.),  Grad(0., 1., -1.),  Grad(0., -1., -1.))

    _p_supply = (151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233,
                 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23,
                 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219,
                 203, 117, 35, 11, 32, 57, 177, 33, 88, 237, 149, 56, 87, 174,
                 20, 125, 136, 171, 168,  68, 175, 74, 165, 71, 134, 139, 48,
                 27, 166, 77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133,
                 230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65,
                 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18,
                 169, 200, 196, 135, 130, 116, 188, 159, 86, 164, 100, 109,
                 198, 173, 186, 3, 64, 52, 217, 226, 250, 124, 123, 5, 202, 38,
                 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16,
                 58, 17, 182, 189, 28, 42, 223, 183, 170, 213, 119, 248, 152,
                 2, 44, 154, 163, 70, 221, 153, 101, 155, 167,  43, 172, 9,
                 129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178,
                 185, 112, 104, 218, 246, 97, 228, 251, 34, 242, 193, 238, 210,
                 144, 12, 191, 179, 162, 241,  81, 51, 145, 235, 249, 14, 239,
                 107, 49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176,
                 115, 121, 50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222,
                 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156,
                 180)

    def __init__(self, seed=None):
        self._p = [v for v in Simplex2D._p_supply]

        self._perm = [None] * 512
        self._permMod12 = [None] * 512

        if 0 < seed < 1:
            seed *= 65536
        seed = Simplex2D.fastfloor(seed)
        if seed < 256:
            seed |= seed << 8

        # random.seed(seed)
        # random.shuffle(self._p)

        for i in range(256):
            v = None
            if i & 1:
                v = self._p[i] ^ (seed & 255)
            else:
                v = self._p[i] ^ ((seed >> 8) & 255)
            self._perm[i] = self._perm[i+256] = v
            self._permMod12[i] = self._permMod12[i+256] = self._grad3[v%12]

    def fastfloor(x):
        xi = int(x)
        return (xi - 1.) if x < xi else xi

    def noise(self, xin, yin):
        s = (xin+yin) * Simplex2D._F2
        i = int(Simplex2D.fastfloor(xin+s))
        j = int(Simplex2D.fastfloor(yin+s))
        t = (i+j) * Simplex2D._G2
        X0 = i-t
        Y0 = j-t
        x0 = xin-X0
        y0 = yin-Y0

        i1, j1 = (1, 0) if x0 > y0 else (0, 1)

        x1 = x0 - i1 + Simplex2D._G2
        y1 = y0 - j1 + Simplex2D._G2
        x2 = x0 - 1. + 2. * Simplex2D._G2
        y2 = y0 - 1. + 2. * Simplex2D._G2

        ii, jj = i & 255, j & 255
        gi0 = self._permMod12[ii+self._perm[jj]]
        gi1 = self._permMod12[ii+i1+self._perm[jj+j1]]
        gi2 = self._permMod12[ii+1+self._perm[jj+1]]

        def calc_part(x, y, gi):
            t = 0.5 - x*x - y*y
            n = 0.
            if t >= 0.:
                t *= t
                n = t * t * gi.dot(x, y)
            return n

        n0 = calc_part(x0, y0, gi0)
        n1 = calc_part(x1, y1, gi1)
        n2 = calc_part(x2, y2, gi2)

        return 70. * (n0 + n1 + n2)







