import math
import numpy as np
# import torch


class BiquadFilter:
    frequency = None
    Q = None
    sampleRate = 48000
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def __init__(self, frequency, Q):
        self.frequency = frequency
        self.Q = Q

    def bandpass(self, inputs):
        w0 = 2 * math.pi * self.frequency / self.sampleRate
        alpha = math.sin(w0) / (2.0 * self.Q)
        b0 = math.sin(w0) / 2
        b1 = 0
        b2 = -math.sin(w0) / 2
        a0 = 1 + alpha
        a1 = -2 * math.cos(w0)
        a2 = 1 - alpha

        y_p1 = 0
        y_p2 = 0
        x_p1 = 0
        x_p2 = 0

        # outputs = torch.zeros(len(inputs)).to(self.device)
        outputs = np.zeros(len(inputs))

        for i in range(len(inputs)):
            x = inputs[i]
            y = ((b0 * x + b1 * x_p1 + b2 * x_p2) - (a1 * y_p1 + a2 * y_p2)) / a0
            outputs[i] = y
            x_p2 = x_p1
            x_p1 = x
            y_p2 = y_p1
            y_p1 = y

        return outputs

