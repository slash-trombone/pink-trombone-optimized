import math
import time
import numpy as np
import random
import utils.interpolation
import vocaltract.vt_model as vt_model

# some parameters that will be used to determine the type of touches
originX = 340
originY = 449
angleOffset = -0.24
angleScale = 0.64
bladeStart = 10
tipStart = 32
lipStart = 39
radius = 298
scale = 60
innerTongueControlRadius = 2.05
outerTongueControlRadius = 3.5
tongueLowerIndexBound = bladeStart + 2
tongueUpperIndexBound = tipStart - 3
n = 44
noseOffset = 0.8
tractCanvasHeight = 600
keyboardTop = 500


# cartesian coordinate system to polar coordinate system
def getXY(index, diameter):
    angle = angleOffset + index * angleScale * math.pi / (lipStart - 1)
    wobble = 0
    angle += wobble
    r = radius - scale * diameter + 100 * wobble
    x = originX - r * math.cos(angle)
    y = originY - r * math.sin(angle)

    return x, y


# polar coordinate system to cartesian coordinate system
def getIndex(x, y):
    xx = x - originX
    yy = y - originY
    angle = math.atan2(yy, xx)
    while angle > 0:
        angle -= 2 * math.pi
    return (math.pi + angle - angleOffset) * (lipStart - 1) / (angleScale * math.pi)


# polar coordinate system to cartesian coordinate system
def getDiameter(x, y):
    xx = x - originX
    yy = y - originY
    return (radius - math.sqrt(xx * xx + yy * yy)) / scale


# code used in the JavaScript based Pink Trombone
# aim at distinguish mouseEvent at tongue area
def judge_tongue(x, y):
    index = getIndex(x, y)
    diameter = getDiameter(x, y)
    return (index >= tongueLowerIndexBound - 4) and (index <= tongueUpperIndexBound + 4) and (
            diameter >= innerTongueControlRadius - 0.5) and (diameter <= outerTongueControlRadius + 0.5)


# code used in the JavaScript based Pink Trombone
# aim at distinguish mouseEvent at glottis area
def judge_glottis(x, y):
    return 20 <= x <= 580 and 520 <= y <= 580


# code used in the JavaScript based Pink Trombone
# aim at distinguish mouseEvent at cavity area
def judge_cavity(x, y):
    index = getIndex(x, y)
    diameter = getDiameter(x, y)
    if diameter < -0.85 - noseOffset:
        return False
    diameter -= 0.3
    if diameter < 0:
        diameter = 0
    judge = (index >= 2) and (index < n) and (y < tractCanvasHeight) and (diameter < 3)
    judge = judge and not judge_tongue(x, y)
    return judge


# randomly new a start point in cavity area
def createOriginCavity():
    x = random.random() * 600
    y = random.random() * 600
    while not judge_cavity(x, y):
        x = random.random() * 600
        y = random.random() * 600
    return x, y


# randomly new a start point in glottis area
def createOriginGlottis():
    x = random.random() * 600
    y = 500 + random.random() * 100

    while not judge_glottis(x, y):
        x = random.random() * 600
        y = 500 + random.random() * 100

    return x, y


# randomly new a start point in tongue area
def createOriginTongue():
    x = random.random() * 600
    y = random.random() * 600
    while not judge_tongue(x, y):
        x = random.random() * 600
        y = random.random() * 600
    return x, y


def randomSign():
    sign = random.random() > 0.5
    if sign:
        return 1
    else:
        return -1


# def createData(filepath, number, sample_length, expected_length):
#     # tongue position
#     tongue_x = [223.80464792356807, 197.55137433781078, 178.47104999719076, 255.90889661765408, 292.2475225387944,
#                 226.00736779526852, 288.3844753978978, 252.68749258256685, 281.57033724156565]
#     tongue_y = [318.1426725176078, 347.34672141562044, 381.6694845483123, 295.52789721926786, 280.64115438648,
#                 383.44140176119674, 328.05336871144453, 350.67006534894534, 383.1974581802828]
#     for i in range(9):
#         origin_tongue_x = tongue_x[i]
#         origin_tongue_y = tongue_y[i]
#         tongue_position = [origin_tongue_x, origin_tongue_y, 1]
#         index = 0
#         positions = []
#         while index < number:
#             origin_cavity_x, origin_cavity_y = createOriginCavity()
#             cavity_position = [origin_cavity_x, origin_cavity_y, 1]
#             cur_position = [tongue_position, cavity_position]
#             positions.append(cur_position)
#
#             for j in range(1, sample_length):
#
#                 cur_cavity_position = cur_position[1]
#                 x_increment = randomSign() * random.random() * 20
#                 y_increment = randomSign() * random.random() * 20
#                 new_x = cur_cavity_position[0] + x_increment
#                 new_y = cur_cavity_position[1] + y_increment
#                 while not judge_cavity(new_x, new_y):
#                     x_increment = randomSign() * random.random() * 20
#                     y_increment = randomSign() * random.random() * 20
#                     new_x = cur_cavity_position[0] + x_increment
#                     new_y = cur_cavity_position[1] + y_increment
#                 cur_cavity_position = [new_x, new_y, 1]
#                 cur_position = [tongue_position, cur_cavity_position]
#                 positions.append(cur_position)
#
#             check = np.array(positions)
#             x = check[:, 1, 0]
#             y = check[:, 1, 1]
#             points = [[x[i], y[i]] for i in range(sample_length)]
#             points = utils.interpolation.tract_interpolation(points, expected_length)
#
#             res = []
#             for j in range(expected_length):
#                 j_cavity_position = [points[j, 0], points[j, 1], 1]
#                 j_res = [tongue_position, j_cavity_position]
#                 res.append(j_res)
#
#             outputs = vt_model.vocal_tract(res, expected_length)
#
#             tongue_inputs_x = [origin_tongue_x for ii in range(sample_length)]
#             tongue_inputs_y = [origin_tongue_y for ii in range(sample_length)]
#             cavity_inputs_x = [positions[ii][1][0] for ii in range(sample_length)]
#             cavity_inputs_y = [positions[ii][1][1] for ii in range(sample_length)]
#             inputs = tongue_inputs_x + tongue_inputs_y + cavity_inputs_x + cavity_inputs_y
#
#             outputs = np.array(outputs)
#             inputs = np.array(inputs)
#
#             filename = str(i) + '_' + str(index) + '.npy'
#             filename_x = filepath + 'pos/' + filename
#             filename_y = filepath + 'audio/' + filename
#             np.save(filename_x, inputs)
#             np.save(filename_y, outputs)
#             index += 1
#             positions = []
#             print(filename)
#
#             # plt.plot(points[:, 0], points[:, 1])
#             # plt.show()
#             # plt.clf()


# varying glottis coordinates (volume and pitch),
# varying tongue coordinates
# and varying lip diameters
def createCompoundDate(filepath, number, sampleLength, expectedLength):
    for i in range(number):
        # cur_tongue_x, cur_tongue_y = origin_tongue_x, origin_tongue_y = createOriginTongue()
        cur_tongue_x, cur_tongue_y = origin_tongue_x, origin_tongue_y = 202.46270831898573, 383.8207594624515
        pos_lst = [[origin_tongue_x, origin_tongue_y]]
        for j in range(1, sampleLength):
            x_increment = randomSign() * random.random() * 50
            y_increment = randomSign() * random.random() * 50
            new_x = cur_tongue_x + x_increment
            new_y = cur_tongue_y + y_increment
            while not judge_tongue(new_x, new_y):
                x_increment = randomSign() * random.random() * 50
                y_increment = randomSign() * random.random() * 50
                new_x = cur_tongue_x + x_increment
                new_y = cur_tongue_y + y_increment
            cur_tongue_x = new_x
            cur_tongue_y = new_y
            pos_lst.append([cur_tongue_x, cur_tongue_y])
        points = utils.interpolation.tract_interpolation(pos_lst, expectedLength)

        glottis_origin_x, glottis_origin_y = cur_glottis_x, cur_glottis_y = 240, 530
        glottis_lst = [[glottis_origin_x, glottis_origin_y]]
        for j in range(1, sampleLength):
            x_increment = randomSign() * random.random() * 50
            y_increment = randomSign() * random.random() * 10
            new_x = cur_glottis_x + x_increment
            new_y = cur_glottis_y + y_increment
            while not judge_glottis(new_x, new_y):
                x_increment = randomSign() * random.random() * 50
                y_increment = randomSign() * random.random() * 10
                new_x = cur_glottis_x + x_increment
                new_y = cur_glottis_y + y_increment
            cur_glottis_x = new_x
            cur_glottis_y = new_y
            glottis_lst.append([cur_glottis_x, cur_glottis_y])
        glottis_points = utils.interpolation.tract_interpolation(glottis_lst, expectedLength)

        pos = []
        train_data = []
        for j in range(expectedLength):
            j_tongue_position = [points[j, 0], points[j, 1], 1]
            j_glottis_position = [glottis_points[j, 0], glottis_points[j, 1], 1]
            half_size = expectedLength / 2
            if j < half_size:
                diameter = 1.5 - j * (1.3 / half_size)
                l_index = 43
                cur_x, cur_y = getXY(l_index, diameter)
                cur_pos = [cur_x, cur_y, 1]

                # cur_glottis_x += x_step
                # cur_glottis_y += y_step
                # cur_glottis_pos = [cur_glottis_x, cur_glottis_y, 1]

                pos.append([cur_pos, j_tongue_position, j_glottis_position])
                train_data.append([diameter, j_tongue_position, j_glottis_position])
            else:
                diameter = 0.2 + (j - half_size) * (1.3 / half_size)
                l_index = 43
                cur_x, cur_y = getXY(l_index, diameter)
                cur_pos = [cur_x, cur_y, 1]

                # cur_glottis_x -= x_step
                # cur_glottis_y -= y_step
                # cur_glottis_pos = [cur_glottis_x, cur_glottis_y, 1]

                pos.append([cur_pos, j_tongue_position, j_glottis_position])
                train_data.append([diameter, j_tongue_position, j_glottis_position])

        outputs = vt_model.vocal_tract(pos, expectedLength)
        outputs = np.array(outputs)

        filepath_audio = filepath + 'audio/' + str(i) + '.npy'
        filepath_pos = filepath + 'pos/' + str(i) + '.npy'

        np.save(filepath_audio, outputs)
        np.save(filepath_pos, train_data)

        print(i)


# varying tongue position while other params remain unchanged
def createTongueDate(filepath, number, sampleLength, expectedLength):
    for i in range(number):
        # cur_tongue_x, cur_tongue_y = origin_tongue_x, origin_tongue_y = createOriginTongue()
        cur_tongue_x, cur_tongue_y = origin_tongue_x, origin_tongue_y = 202.46270831898573, 383.8207594624515
        pos_lst = [[origin_tongue_x, origin_tongue_y]]
        for j in range(1, sampleLength):
            x_increment = randomSign() * random.random() * 50
            y_increment = randomSign() * random.random() * 50
            new_x = cur_tongue_x + x_increment
            new_y = cur_tongue_y + y_increment
            while not judge_tongue(new_x, new_y):
                x_increment = randomSign() * random.random() * 50
                y_increment = randomSign() * random.random() * 50
                new_x = cur_tongue_x + x_increment
                new_y = cur_tongue_y + y_increment
            cur_tongue_x = new_x
            cur_tongue_y = new_y
            pos_lst.append([cur_tongue_x, cur_tongue_y])
        points = utils.interpolation.tract_interpolation(pos_lst, expectedLength)
        pos = []
        for j in range(expectedLength):
            j_tongue_position = [[points[j, 0], points[j, 1], 1]]
            pos.append(j_tongue_position)
        start_time = time.time()
        outputs = vt_model.vocal_tract(pos, expectedLength)
        end_time = time.time()
        print('time cost: ', end_time - start_time, 's')
        outputs = np.array(outputs)
        # outputs = outputs.cpu().numpy()

        filepath_audio = filepath + 'audio/' + str(i) + '.npy'
        filepath_pos = filepath + 'pos/' + str(i) + '.npy'

        np.save(filepath_audio, outputs)
        np.save(filepath_pos, pos)

        # jsonFile = {"content": pos}
        # b = json.dumps(jsonFile)
        # f2 = open(filepath + str(i) + '.json', 'w')
        # f2.write(b)
        # f2.close()

        print(i)


# varying lip diameter value
# lip diameter is used to describe the way mouth is opened, wide open or closed
# tongue_x and tongue_y are coordinates of different vowels
# sets of data are generated with different vowels, for each set,
# varying lip diameter values and other params remain unchanged
def createLipData(filepath, number, sampleLength, expectedLength):
    tongue_x = [223.80464792356807, 197.55137433781078, 178.47104999719076, 255.90889661765408, 292.2475225387944,
                226.00736779526852, 288.3844753978978, 252.68749258256685, 281.57033724156565]
    tongue_y = [318.1426725176078, 347.34672141562044, 381.6694845483123, 295.52789721926786, 280.64115438648,
                383.44140176119674, 328.05336871144453, 350.67006534894534, 383.1974581802828]
    for i in range(9):
        o_tongue_x = tongue_x[i]
        o_tongue_y = tongue_y[i]
        for index in range(number):
            x_increment = randomSign() * random.random() * 10
            y_increment = randomSign() * random.random() * 10
            new_x = o_tongue_x + x_increment
            new_y = o_tongue_y + y_increment
            while not judge_tongue(new_x, new_y):
                x_increment = randomSign() * random.random() * 10
                y_increment = randomSign() * random.random() * 10
                new_x = o_tongue_x + x_increment
                new_y = o_tongue_y + y_increment
            tongue_position = [new_x, new_y, 1]

            positions = []
            train_data = []
            for cnt in range(expectedLength):
                diameter = 1.5 - cnt * (1.5 / expectedLength)
                l_index = 43
                cur_x, cur_y = getXY(l_index, diameter)
                cur_pos = [cur_x, cur_y, 1]
                positions.append([cur_pos, tongue_position])
                train_data.append([diameter, tongue_position])

            outputs = vt_model.vocal_tract(positions, expectedLength)
            outputs = np.array(outputs)

            filepath_audio = filepath + 'audio/' + str(i) + '_' + str(index) + '.npy'
            filepath_pos = filepath + 'pos/' + str(i) + '_' + str(index) + '.npy'

            np.save(filepath_audio, outputs)
            np.save(filepath_pos, train_data)
            print(i, index)


# varying volume value
# other params remain unchanged
def createLoudnessData(filepath, number, expectedLength):
    step = 60 / (48000 * 3)
    positions = []

    for i in range(number):
        x_pos = random.random() * 600
        y_pos = 520
        for j in range(expectedLength):
            cur_pos = [[x_pos, y_pos, 1]]
            positions.append(cur_pos)
            y_pos += step
        outputs = vt_model.vocal_tract(positions, expectedLength)
        outputs = np.array(outputs)
        positions = np.array(positions)
        filepath_pos = filepath + '/pos/' + str(i) + '.npy'
        filepath_audio = filepath + '/audio/' + str(i) + '.npy'
        np.save(filepath_pos, positions)
        np.save(filepath_audio, outputs)
        print(i)
        positions = []


# varying pitch value
# other params remain unchanged
def createPitchData(filepath, number, expectedLength):
    step = 600 / (48000 * 3)
    positions = []

    for i in range(number):
        x_pos = 0
        y_pos = 550 + random.random() * 30 * randomSign()
        for j in range(expectedLength):
            cur_pos = [[x_pos, y_pos, 1]]
            positions.append(cur_pos)
            x_pos += step
        outputs = vt_model.vocal_tract(positions, expectedLength)
        outputs = np.array(outputs)
        positions = np.array(positions)
        filepath_pos = filepath + '/pos/' + str(i) + '.npy'
        filepath_audio = filepath + '/audio/' + str(i) + '.npy'
        np.save(filepath_pos, positions)
        np.save(filepath_audio, outputs)
        print(i)
        positions = []


# filepath = '../../data/pitch_1/'
# createPitchData(filepath, 100, 48000*3)


filepath = './tongue/'
createTongueDate(filepath, 2, 50, 48000 * 2)
