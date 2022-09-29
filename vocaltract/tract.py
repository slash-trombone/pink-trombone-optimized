from math import atan2, pow, floor, sqrt, cos, pi, ceil

import numpy as np
from utils.my_math import clamp, moveTowards
# from numba import jit

class Tract:
    sampleRate = 48000
    n = 44
    bladeStart = 10
    tipStart = 32
    lipStart = 39
    R = []
    L = []
    reflection = []
    newReflection = []
    junctionOutputR = []
    junctionOutputL = []
    diameter = []
    restDiameter = []
    targetDiameter = []
    newDiameter = []
    A = []
    glottalReflection = 0.75
    lipReflection = -0.85
    lastObstruction = -1
    fade = 1.0
    movementSpeed = 15
    transients = []
    lipOutput = 0
    noseOutput = 0
    velumTarget = 0.01

    noseLength = 28
    noseStart = 17
    noseR = None
    noseL = None
    noseJunctionOutputR = None
    noseJunctionOutputL = None
    noseReflection = None
    noseDiameter = None
    noseA = None
    newReflectionLeft = None
    newReflectionRight = None
    newReflectionNose = None
    reflectionLeft = None
    reflectionRight = None
    reflectionNose = None

    originX = 340
    originY = 449
    angleOffset = -0.24
    angleScale = 0.64
    radius = 298
    scale = 60
    tongueIndex = 12.9
    tongueDiameter = 2.43
    innerTongueControlRadius = 2.05
    outerTongueControlRadius = 3.5
    tongueTouch = 0
    tongueLowerIndexBound = None
    tongueUpperIndexBound = None
    tongueIndexCentre = None
    gridOffset = 1.7
    noseOffset = 0.8

    touches = []
    glottis = None

    def __init__(self, glottis):
        n_g = self.n
        noseLength_g = self.noseLength

        self.diameter = np.zeros(n_g)
        self.restDiameter = np.zeros(n_g)
        self.targetDiameter = np.zeros(n_g)
        self.newDiameter = np.zeros(n_g)
        for i in range(n_g):
            diameter = 0
            if i < 6.5:
                diameter = 0.6
            elif i < 12:
                diameter = 1.1
            else:
                diameter = 1.5
            self.diameter[i] = self.restDiameter[i] = self.targetDiameter[i] = self.newDiameter[i] = diameter

        self.R = np.zeros(n_g)
        self.L = np.zeros(n_g)
        self.reflection = np.zeros(n_g + 1)
        self.newReflection = np.zeros(n_g + 1)
        self.junctionOutputR = np.zeros(n_g + 1)
        self.junctionOutputL = np.zeros(n_g + 1)
        self.A = np.zeros(n_g)

        self.noseR = np.zeros(noseLength_g)
        self.noseL = np.zeros(noseLength_g)
        self.noseJunctionOutputR = np.zeros(noseLength_g + 1)
        self.noseJunctionOutputL = np.zeros(noseLength_g + 1)
        self.noseReflection = np.zeros(noseLength_g + 1)
        self.noseDiameter = np.zeros(noseLength_g)
        self.noseA = np.zeros(noseLength_g)
        for i in range(noseLength_g):
            diameter = 0
            d = 2 * (i / noseLength_g)
            if d < 1:
                diameter = 0.4 + 1.6 * d
            else:
                diameter = 0.5 + 1.5 * (2 - d)
            diameter = min(diameter, 1.9)
            self.noseDiameter[i] = diameter

        self.newReflectionLeft = 0
        self.newReflectionRight = 0
        self.newReflectionNose = 0

        self.calculateReflections()
        self.calculateNoseReflections()
        self.noseDiameter[0] = self.velumTarget

        self.setRestDiameter()
        for i in range(self.n):
            self.diameter[i] = self.targetDiameter[i] = self.restDiameter[i]
        self.tongueLowerIndexBound = self.bladeStart + 2
        self.tongueUpperIndexBound = self.tipStart - 3
        self.tongueIndexCentre = 0.5 * (self.tongueLowerIndexBound + self.tongueUpperIndexBound)

        # pass glottis to current environment
        self.glottis = glottis

    def reshapeTract(self, deltaTime):
        movementSpeed_g = self.movementSpeed
        n_g = self.n
        diameter_g = self.diameter
        targetDiameter_g = self.targetDiameter
        noseStart_g = self.noseStart
        tipStart_g = self.tipStart
        lastObstruction_g = self.lastObstruction
        noseA_g = self.noseA
        addTransient_g = self.addTransient
        noseDiameter_g = self.noseDiameter
        velumTarget_g = self.velumTarget

        amount = deltaTime * movementSpeed_g
        newLastObstruction = -1
        for i in range(n_g):
            diameter = diameter_g[i]
            targetDiameter = targetDiameter_g[i]
            if diameter <= 0:
                newLastObstruction = i
            slowReturn = None
            if i < noseStart_g:
                slowReturn = 0.6
            elif i >= tipStart_g:
                slowReturn = 1.0
            else:
                slowReturn = 0.6 + 0.4 * (i - noseStart_g) / (tipStart_g - noseStart_g)
            diameter_g[i] = moveTowards(diameter, targetDiameter, slowReturn * amount, 2 * amount)
        if lastObstruction_g > -1 and newLastObstruction == -1 and noseA_g[0] < 0.05:
            addTransient_g(lastObstruction_g)
        lastObstruction_g = newLastObstruction

        amount = deltaTime * movementSpeed_g
        noseDiameter_g[0] = moveTowards(noseDiameter_g[0], velumTarget_g, amount * 0.25, amount * 0.1)
        noseA_g[0] = noseDiameter_g[0] * noseDiameter_g[0]

    def finishBlock(self):
        self.reshapeTract(512 / 48000)
        self.calculateReflections()

    def calculateReflections(self):
        n_g = self.n
        A_g = self.A
        noseA_g = self.noseA
        diameter_g = self.diameter
        newReflection_g = self.newReflection
        reflection_g = self.reflection
        noseStart_g = self.noseStart

        # for i in range(n_g):
        #     A_g[i] = diameter_g[i] * diameter_g[i]
        A_g = np.square(diameter_g)
        for i in range(1, n_g):
            reflection_g[i] = newReflection_g[i]
            if A_g[i] == 0:
                newReflection_g[i] = 0.999
            else:
                newReflection_g[i] = (A_g[i-1] - A_g[i]) / (A_g[i-1] + A_g[i])

        self.reflectionLeft = self.newReflectionLeft
        self.reflectionRight = self.newReflectionRight
        self.reflectionNose = self.newReflectionNose
        p_sum = A_g[noseStart_g] + A_g[noseStart_g + 1] + noseA_g[0]
        self.newReflectionLeft = (2 * A_g[noseStart_g] - p_sum) / p_sum
        self.newReflectionRight = (2 * A_g[noseStart_g + 1] - p_sum) / p_sum
        self.newReflectionNose = (2 * noseA_g[0] - p_sum) / p_sum

    def calculateNoseReflections(self):
        noseA_g = self.noseA
        noseDiameter_g = self.noseDiameter
        noseLength_g = self.noseLength
        noseReflection_g = self.noseReflection

        noseA_g = np.square(noseDiameter_g)
        noseReflection_g[1:noseLength_g] = (noseA_g[:noseLength_g - 1] - noseA_g[1:noseLength_g]) / (
                    noseA_g[:noseLength_g - 1] + noseA_g[1:noseLength_g])


    def runStep(self, glottalOutput, turbulenceNoise, p_lambda):
        L_g = self.L
        R_g = self.R
        n_g = self.n
        reflection_g = self.reflection
        newReflection_g = self.newReflection
        junctionOutputR_g = self.junctionOutputR
        junctionOutputL_g = self.junctionOutputL
        lipReflection_g = self.lipReflection
        noseR_g = self.noseR
        noseL_g = self.noseL
        noseLength_g = self.noseLength
        fade_g = self.fade
        noseJunctionOutputL_g = self.noseJunctionOutputL
        noseJunctionOutputR_g = self.noseJunctionOutputR
        noseReflection_g = self.noseReflection

        self.processTransients()
        self.addTurbulenceNoise(turbulenceNoise)

        junctionOutputR_g[0] = L_g[0] * self.glottalReflection + glottalOutput
        junctionOutputL_g[n_g] = R_g[n_g - 1] * lipReflection_g

        self.calculateJunctions(p_lambda)

        i = self.noseStart
        r = self.newReflectionLeft * (1 - p_lambda) + self.reflectionLeft * p_lambda
        junctionOutputL_g[i] = r * R_g[i - 1] + (1 + r) * (noseL_g[0] + L_g[i])
        r = self.newReflectionRight * (1 - p_lambda) + self.reflectionRight * p_lambda
        junctionOutputR_g[i] = r * L_g[i] + (1 + r) * (R_g[i - 1] + noseL_g[0])
        r = self.newReflectionNose * (1 - p_lambda) + self.reflectionNose * p_lambda
        noseJunctionOutputR_g[0] = r * noseL_g[0] + (1 + r) * (L_g[i] + R_g[i - 1])

        self.calculateLipOutput()

        noseJunctionOutputL_g[noseLength_g] = noseR_g[noseLength_g - 1] * lipReflection_g

        self.calculateNoseJunctions()

        self.calculateNoseOutput()


    def calculateNoseOutput(self):
        self.noseR[:self.noseLength] = self.noseJunctionOutputR[:self.noseLength] * self.fade
        self.noseL[:self.noseLength] = self.noseJunctionOutputL[1:self.noseLength + 1] * self.fade
        self.noseOutput = self.noseR[self.noseLength - 1]

    # @staticmethod
    # @jit(nopython=True)
    # def n_cal_nose_junc(nose_refl, nose_len, nose_r, nose_l):
    #     w = nose_refl[1:nose_len] * (nose_r[:nose_len-1] + nose_l[1:nose_len])
    #     nose_junc_o_r, nose_junc_o_l = nose_r[:nose_len-1]-w, nose_l[1:nose_len]+w
    #     return nose_junc_o_r, nose_junc_o_l

    def calculateNoseJunctions(self):
        # self.noseJunctionOutputR[1:self.noseLength], self.noseJunctionOutputL[1:self.noseLength] = \
        #     self.n_cal_nose_junc(self.noseReflection, self.noseLength, self.noseR, self.noseL)
        w = self.noseReflection[1:self.noseLength] * (self.noseR[:self.noseLength - 1] + self.noseL[1:self.noseLength])
        self.noseJunctionOutputR[1:self.noseLength], self.noseJunctionOutputL[1:self.noseLength] = self.noseR[:self.noseLength - 1] - w, self.noseL[1:self.noseLength] + w

    # @staticmethod
    # @jit(nopython=True)
    # def n_cal_junc(refl, n, p_lambda, new_refl, R, L):
    #     r = refl[1:n] * (1-p_lambda) + new_refl[1:n] * p_lambda
    #     w = r * (R[:n-1] + L[1:n])
    #     junc_o_r, junc_o_l = R[:n-1]-w, L[1:n]+w
    #     return junc_o_r, junc_o_l


    def calculateJunctions(self, p_lambda):
        # self.junctionOutputR[1:self.n], self.junctionOutputL[1:self.n] = \
        #     self.n_cal_junc(self.reflection, self.n, p_lambda, self.newReflection, self.R, self.L)
        r = self.reflection[1:self.n] * (1 - p_lambda) + self.newReflection[1:self.n] * p_lambda
        w = r * (self.R[:self.n - 1] + self.L[1:self.n])
        self.junctionOutputR[1:self.n], self.junctionOutputL[1:self.n] = self.R[:self.n-1] - w, self.L[1:self.n] + w


    def calculateLipOutput(self):
        self.R[:] = self.junctionOutputR[:-1] * 0.999
        self.L[:] = self.junctionOutputL[1:] * 0.999
        self.lipOutput = self.R[-1]


    def addTransient(self, position):
        trans = {'position': position, 'timeAlive': 0, 'lifeTime': 0.2, 'strength': 0.3, 'exponent': 200}
        self.transients.append(trans)


    def processTransients(self):
        R_g = self.R
        L_g = self.L
        transients_g = self.transients
        sampleRate_g = self.sampleRate

        for i in range(len(transients_g)):
            trans = transients_g[i]
            amplitude = trans['strength'] * pow(2, -trans['exponent'] * trans['timeAlive'])
            R_g[trans['position']] += amplitude / 2
            L_g[trans['position']] += amplitude / 2
            trans['timeAlive'] += 1.0 / (sampleRate_g * 2)
        for i in range(len(transients_g) - 1, -1):
            trans = transients_g[i]
            if trans['timeAlive'] > trans['lifeTime']:
                transients_g.pop(i)

    def addTurbulenceNoise(self, turbulenceNoise):
        getIndex_g = self.getIndex
        getDiameter_g = self.getDiameter
        addTurbulenceNoiseAtIndex_g = self.addTurbulenceNoiseAtIndex
        n_g = self.n
        touches_g = self.touches

        for j in range(len(touches_g)):
            touch = touches_g[j]
            x, y = touch[0], touch[1]
            index = getIndex_g(x, y)
            diameter = getDiameter_g(x, y)
            if index < 2 or index > n_g - 2 or diameter <= 0:
                continue
            # if diameter <= 0:
            #     continue
            addTurbulenceNoiseAtIndex_g(0.66 * turbulenceNoise * touch[2], index, diameter)

    def addTurbulenceNoiseAtIndex(self, turbulenceNoise, index, diameter):
        R_g = self.R
        L_g = self.L

        i = floor(index)
        delta = index - i
        turbulenceNoise *= self.glottis.getNoiseModulator()
        thinness0 = clamp(8 * (0.7 - diameter), 0, 1)
        openness = clamp(30 * (diameter - 0.3), 0, 1)
        noise0 = turbulenceNoise * (1 - delta) * thinness0 * openness
        noise1 = turbulenceNoise * delta * thinness0 * openness
        R_g[i + 1] += noise0 / 2
        L_g[i + 1] += noise0 / 2
        R_g[i + 2] += noise1 / 2
        L_g[i + 2] += noise1 / 2

    def getIndex(self, x, y):
        xx = x - self.originX
        yy = y - self.originY
        angle = atan2(yy, xx)
        while angle > 0:
            angle -= 2 * pi
        return (pi + angle - self.angleOffset) * (self.lipStart - 1) / (self.angleScale * pi)

    def getDiameter(self, x, y):
        xx = x - self.originX
        yy = y - self.originY
        return (self.radius - sqrt(xx * xx + yy * yy)) / self.scale

    def setRestDiameter(self):
        bladeStart_g = self.bladeStart
        lipStart_g = self.lipStart
        tipStart_g = self.tipStart
        restDiameter_g = self.restDiameter
        tongueIndex_g = self.tongueIndex
        tongueDiameter_g = self.tongueDiameter
        gridOffset_g = self.gridOffset

        for i in range(bladeStart_g, lipStart_g):
            t = 1.1 * pi * (tongueIndex_g - i) / (tipStart_g - bladeStart_g)
            fixedTongueDiameter = 2 + (tongueDiameter_g - 2) / 1.5
            curve = (1.5 - fixedTongueDiameter + gridOffset_g) * cos(t)
            if (i == bladeStart_g - 2) or (i == lipStart_g - 1):
                curve *= 0.8
            if (i == bladeStart_g) or (i == lipStart_g - 2):
                curve *= 0.94
            restDiameter_g[i] = 1.5 - curve

    def handleTouches(self, cur_touches):
        tongueTouch_g = self.tongueTouch
        getIndex_g = self.getIndex
        getDiameter_g = self.getDiameter
        tongueLowerIndexBound_g = self.tongueLowerIndexBound
        tongueUpperIndexBound_g = self.tongueUpperIndexBound
        innerTongueControlRadius_g = self.innerTongueControlRadius
        outerTongueControlRadius_g = self.outerTongueControlRadius
        n_g = self.n
        setRestDiameter_g = self.setRestDiameter
        noseStart_g = self.noseStart
        noseOffset_g = self.noseOffset
        tipStart_g = self.tipStart
        targetDiameter_g = self.targetDiameter
        velumTarget_g = self.velumTarget
        restDiameter_g = self.restDiameter

        tractCanvasHeight = 600
        if tongueTouch_g != 0:
            tongueTouch_g = 0

        if tongueTouch_g == 0:
            for j in range(len(cur_touches)):
                touch = cur_touches[j]
                # if touch[2] == 1:
                #     continue
                x, y = touch[0], touch[1]
                index = getIndex_g(x, y)
                diameter = getDiameter_g(x, y)
                if (index >= tongueLowerIndexBound_g - 4) and (index <= tongueUpperIndexBound_g + 4) and (
                        diameter >= innerTongueControlRadius_g - 0.5) and (
                        diameter <= outerTongueControlRadius_g + 0.5):
                    tongueTouch_g = touch

        if tongueTouch_g != 0:
            x, y = tongueTouch_g[0], tongueTouch_g[1]
            index = getIndex_g(x, y)
            diameter = getDiameter_g(x, y)
            fromPoint = (outerTongueControlRadius_g - diameter) / (
                        outerTongueControlRadius_g - innerTongueControlRadius_g)
            fromPoint = clamp(fromPoint, 0, 1)
            fromPoint = pow(fromPoint, 0.58) - 0.2 * (fromPoint * fromPoint - fromPoint)
            self.tongueDiameter = clamp(diameter, innerTongueControlRadius_g, outerTongueControlRadius_g)
            out = fromPoint * 0.5 * (tongueUpperIndexBound_g - tongueLowerIndexBound_g)
            self.tongueIndex = clamp(index, self.tongueIndexCentre - out, self.tongueIndexCentre + out)

        setRestDiameter_g()
        for i in range(n_g):
            targetDiameter_g[i] = restDiameter_g[i]
        # targetDiameter_g = restDiameter_g.copy()
        self.velumTarget = 0.01
        for i in range(len(cur_touches)):
            touch = cur_touches[i]
            x = touch[0]
            y = touch[1]
            index = getIndex_g(x, y)
            diameter = getDiameter_g(x, y)
            if (index > noseStart_g) and (diameter < -noseOffset_g):
                velumTarget_g = 0.4
            if diameter < -0.85 - noseOffset_g:
                continue
            diameter -= 0.3
            if diameter < 0:
                diameter = 0
            width = 2
            if index < 25:
                width = 10
            elif index >= tipStart_g:
                width = 5
            else:
                width = 10 - 5 * (index - 25) / (tipStart_g - 25)
            if (index >= 2) and (index < n_g) and (y < tractCanvasHeight) and (diameter < 3):
                intIndex = round(index)
                for j in range(-ceil(width) - 1, ceil(width) + 1):
                    if (intIndex + j < 0) or (intIndex + j >= n_g):
                        continue
                    relpos = (intIndex + j) - index
                    relpos = abs(relpos) - 0.5
                    shrink = None
                    if relpos <= 0:
                        shrink = 0
                    elif relpos > width:
                        shrink = 1
                    else:
                        shrink = 0.5 * (1 - cos(pi * relpos / width))
                    if diameter < targetDiameter_g[intIndex + j]:
                        targetDiameter_g[intIndex + j] = diameter + (
                                    targetDiameter_g[intIndex + j] - diameter) * shrink
