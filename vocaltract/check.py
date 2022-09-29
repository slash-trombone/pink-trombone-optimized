# import json
#
# filename_2 = 'params/0.json'
# with open(filename_2, encoding='utf8') as load_f:
#     param_files = json.load(load_f)
#     diameters = [[0 for i in range(88200)] for j in range(44)]
#     for i in range(len(param_files)):
#         param_file = param_files[i]
#         for j in range(44):
#             diameters[j][i] = param_file['diameter'][j]
#
#
# import matplotlib.pyplot as plt
#
# x = range(88200)
# y = diameters[22]
# l1 = plt.scatter(x, y, linewidths=0.0001, marker='.')
# plt.show()


#
# import random
#
# import numpy as np
#
# from vocaltract.BiquadFilter import BiquadFilter
#
#
# def createWhiteNoise(frameCount):
#     whiteNoise = np.zeros(frameCount)
#     for i in range(len(whiteNoise)):
#         whiteNoise[i] = random.random()
#     return whiteNoise
#
#
# # not used for now
# def startSound(length):
#     whiteNoise = createWhiteNoise(length)
#     aspireFilter = BiquadFilter(500, 0.5)
#     fricativeFilter = BiquadFilter(1000, 0.5)
#     aspireOutput = aspireFilter.bandpass(whiteNoise)
#     fricativeOutput = fricativeFilter.bandpass(whiteNoise)
#     print('a')
#
#
# startSound(48000)
import math

angleOffset = -0.24
angleScale = 0.64
lipStart = 39
radius = 298
scale = 60
originX = 340
originY = 449
tongueIndexCenter = 20.5
a = 2.05
b = 2.775
c = 3.5


def circle(i1, d):
    angle = angleOffset + i1 * angleScale * math.pi / (lipStart - 1)
    r = radius - scale * d
    x1 = originX - r * math.cos(angle)
    y1 = originY - r * math.sin(angle)
    return x1, y1


ii = [tongueIndexCenter, tongueIndexCenter-4.25, tongueIndexCenter-8.5, tongueIndexCenter+4.25, tongueIndexCenter+8.5, tongueIndexCenter-6.1, tongueIndexCenter+6.1, tongueIndexCenter, tongueIndexCenter]
dd = [a, a, a, a, a, b, b, b, c]

result_X = []
result_Y = []
for i in range(9):
    x, y = circle(ii[i], dd[i])
    result_X.append(x)
    result_Y.append(y)

a = 3


