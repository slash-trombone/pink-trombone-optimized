import numpy as np
import math
from scipy.interpolate import splrep, splev


def tract_interpolation(points, expectedNumber):
    number = len(points)
    step = math.ceil(expectedNumber / number)
    count = []
    index = 0
    for point in points:
        count.append(index)
        index += step
    if count[-1] != expectedNumber - 1:
        count[-1] = expectedNumber - 1
    count = np.array(count)

    x_sample = np.array([point[0] for point in points])
    y_sample = np.array([point[1] for point in points])

    tck_x = splrep(count, x_sample)
    tck_y = splrep(count, y_sample)
    count_new = np.arange(0, expectedNumber, 1)
    x_new = splev(count_new, tck_x).tolist()
    y_new = splev(count_new, tck_y).tolist()

    tract = []
    for i in range(expectedNumber):
        tract.append([x_new[i], y_new[i]])
    tract = np.array(tract)
    return tract
