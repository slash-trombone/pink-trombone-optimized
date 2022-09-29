from math import pow, cos, pi, exp, sin, log, sqrt
from utils.my_math import clamp
from utils import simplex


class Glottis:
    sampleRate = 48000

    timeInWaveform = 0
    oldFrequency = 140
    newFrequency = 140
    UIFrequency = 140
    smoothFrequency = 140
    oldTenseness = 0.6
    newTenseness = 0.6
    UITenseness = 0.6
    totalTime = 0
    vibratoAmount = 0.005
    vibratoFrequency = 6
    intensity = 0
    loudness = 1

    isTouched = False
    touch = 0
    x = 240
    y = 530
    semitones = 20
    baseNote = 87.3071

    keyboardTop = 500
    keyboardLeft = 00
    keyboardWidth = 600
    keyboardHeight = 100

    noise = simplex.Simplex2D(seed=27)

    frequency = None
    Rd = None
    waveformLength = None
    alpha = None
    E0 = None
    epsilon = None
    shift = None
    Delta = None
    Te = None
    omega = None

    def __init__(self):
        self.setup_waveform(0)

    def handleTouches(self, cur_touches):
        if self.touch != 0:
            self.touch = 0
        if self.touch == 0:
            for j in range(len(cur_touches)):
                touch = cur_touches[j]
                if touch[1] < self.keyboardTop:
                    continue
                self.touch = touch
        if self.touch != 0:
            local_y = self.touch[1] - self.keyboardTop - 10
            local_x = self.touch[0] - self.keyboardLeft
            local_y = clamp(local_y, 0, self.keyboardHeight-26)
            semitone = self.semitones * local_x / self.keyboardWidth + 0.5
            self.UIFrequency = self.baseNote * pow(2, semitone/12)
            if self.intensity == 0:
                self.smoothFrequency = self.UIFrequency
            t = clamp(1-local_y/(self.keyboardHeight-28), 0, 1)
            self.UITenseness = 1 - cos(t * pi * 0.5)
            self.loudness = pow(self.UITenseness, 0.25)
            self.x = self.touch[0]
            self.y = local_y + self.keyboardTop + 10
        self.isTouched = (self.touch != 0)

    def setup_waveform(self, p_lambda):
        self.frequency = self.oldFrequency * (1 - p_lambda) + self.newFrequency * p_lambda
        tenseness = self.oldTenseness * (1 - p_lambda) + self.newTenseness * p_lambda
        self.Rd = 3 * (1 - tenseness)
        self.waveformLength = 1.0 / self.frequency

        Rd = self.Rd
        if Rd < 0.5:
            Rd = 0.5
        elif Rd > 2.7:
            Rd = 2.7

        Ra = -0.01 + 0.048 * Rd
        Rk = 0.224 + 0.118 * Rd
        Rg = (Rk / 4) * (0.5 + 1.2 * Rk) / (0.11 * Rd - Ra * (0.5 + 1.2 * Rk))

        Ta = Ra
        Tp = 1 / (2 * Rg)
        Te = Tp + Tp * Rk

        epsilon = 1 / Ta
        shift = exp(-epsilon * (1 - Te))
        Delta = 1 - shift

        RHSIntegral = (1 / epsilon) * (shift - 1) + (1 - Te) * shift
        RHSIntegral = RHSIntegral / Delta

        totalLowerIntegral = - (Te - Tp) / 2 + RHSIntegral
        totalUpperIntegral = -totalLowerIntegral

        omega = pi / Tp
        s = sin(omega * Te)

        y = -pi * s * totalUpperIntegral / (Tp * 2)
        z = log(y)
        alpha = z / (Tp / 2 - Te)
        E0 = -1 / (s * exp(alpha * Te))

        self.alpha = alpha
        self.E0 = E0
        self.epsilon = epsilon
        self.shift = shift
        self.Delta = Delta
        self.Te = Te
        self.omega = omega

    def runStep(self, p_lambda, noiseSource):
        timeStep = 1 / self.sampleRate
        self.timeInWaveform += timeStep
        self.totalTime += timeStep
        if self.timeInWaveform > self.waveformLength:
            self.timeInWaveform -= self.waveformLength
            self.setup_waveform(p_lambda)
        out = self.normalizedLFWaveform(self.timeInWaveform/self.waveformLength)
        aspiration = self.intensity * (1-sqrt(self.UITenseness)) * self.getNoiseModulator() * noiseSource
        aspiration *= 0.2 + 0.02 * self.noise.noise(self.totalTime*1.99*1.2, -self.totalTime*1.99*0.7)
        out += aspiration
        return out

    def getNoiseModulator(self):
        voiced = 0.1 + 0.2 * max(0, sin(pi * 2 * self.timeInWaveform / self.waveformLength))
        return self.UITenseness * self.intensity * voiced + (1 - self.UITenseness * self.intensity) * 0.3

    def normalizedLFWaveform(self, t):
        if t > self.Te:
            output = (-exp(-self.epsilon * (t-self.Te)) + self.shift)/self.Delta
        else:
            output = self.E0 * exp(self.alpha*t) * sin(self.omega * t)
        return output * self.intensity * self.loudness

    def finishBlock(self):
        vibrato = 0
        vibrato += self.vibratoAmount * sin(2 * pi * self.totalTime * self.vibratoFrequency)
        vibrato += 0.02 * self.noise.noise(self.totalTime * 4.07 * 1.2, -self.totalTime * 4.07 * 0.7)
        vibrato += 0.04 * self.noise.noise(self.totalTime * 2.15 * 1.2, -self.totalTime * 2.15 * 0.7)

        # wobble
        # vibrato += 0.2 * self.noise.noise(self.totalTime * 0.98 * 1.2, -self.totalTime * 0.98 * 0.7)
        # vibrato += 0.4 * self.noise.noise(self.totalTime * 0.5 * 1.2, -self.totalTime * 0.5 * 0.7)

        if self.UIFrequency > self.smoothFrequency:
            self.smoothFrequency = min(self.smoothFrequency * 1.1, self.UIFrequency)
        if self.UIFrequency < self.smoothFrequency:
            self.smoothFrequency = max(self.smoothFrequency / 1.1, self.UIFrequency)
        self.oldFrequency = self.newFrequency
        self.newFrequency = self.smoothFrequency * (1 + vibrato)
        self.oldTenseness = self.newTenseness
        self.newTenseness = self.UITenseness + 0.1 * self.noise.noise(self.totalTime * 0.46 * 1.2, -self.totalTime * 0.46 * 0.7) + 0.05 * self.noise.noise(self.totalTime * 0.36 * 1.2, -self.totalTime * 0.36 * 0.7)
        if not self.isTouched:
            self.newTenseness += (3 - self.UITenseness) * (1 - self.intensity)
        self.intensity += 0.13
        self.intensity = clamp(self.intensity, 0, 1)

