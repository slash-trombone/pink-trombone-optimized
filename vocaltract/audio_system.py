import numpy as np
# import torch
from vocaltract.BiquadFilter import BiquadFilter



class AudioSystem:
    sampleRate = 48000
    blockLength = 512
    blockTime = 1
    touches = []
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # updates = []

    def __init__(self, my_glottis, my_tract, touches):
        self.blockTime = self.blockLength / self.sampleRate
        self.pt_glottis = my_glottis
        self.pt_tract = my_tract
        self.touches = touches
        # self.updates = updates

    # We do not use this for now, just read input values from a pre-recorded json file
    def createWhiteNoise(self, frameCount):
        # whiteNoise = torch.rand(frameCount).to(self.device)
        whiteNoise = np.random.rand(frameCount)
        return whiteNoise

    # not used for now
    def startSound(self, frameCount):
        whiteNoise = self.createWhiteNoise(frameCount)
        aspireFilter = BiquadFilter(500, 0.5)
        fricativeFilter = BiquadFilter(1000, 0.5)
        aspireOutput = aspireFilter.bandpass(whiteNoise)
        fricativeOutput = fricativeFilter.bandpass(whiteNoise)
        # start_time = time.time()
        output = self.pt_processor(aspireOutput, fricativeOutput)
        # end_time = time.time()
        # print('time cost: ', end_time - start_time, 's')
        return output

    # input values is directly passed to this function
    # def startSound(self, inputValues):
    #     aspireOutput = inputValues
    #     fricativeOutput = inputValues
    #     output, diameters = self.pt_processor(aspireOutput, fricativeOutput)
    #     return output, diameters

    # processor
    def pt_processor(self, aspireOutput, fricativeOutput):
        inputArray1 = aspireOutput
        inputArray2 = fricativeOutput
        outArray = np.zeros(len(inputArray1))

        # diameters = [[0 for i in range(88200)] for j in range(44)]

        for j in range(len(inputArray1)):
            self.pt_tract.touches = self.touches[j]

            # for i in range(44):
            #     diameters[i][j] = self.pt_tract.diameter[i]

            # in javascript version, input values are packed into buffers, the size of buffer is 512
            lambda1 = (j % 512) / 512
            lambda2 = ((j % 512) + 0.5) / 512

            # start_time = time.time()
            glottalOutput = self.pt_glottis.runStep(lambda1, inputArray1[j])
            # end_time = time.time()
            # print('glottal time cost: ', end_time - start_time, 's')

            vocalOutput = 0
            # start_time = time.time()
            self.pt_tract.runStep(glottalOutput, inputArray2[j], lambda1)
            vocalOutput += self.pt_tract.lipOutput + self.pt_tract.noseOutput
            self.pt_tract.runStep(glottalOutput, inputArray2[j], lambda2)
            vocalOutput += self.pt_tract.lipOutput + self.pt_tract.noseOutput
            # end_time = time.time()
            # print('vocal time cost: ', end_time - start_time, 's')
            outArray[j] = vocalOutput * 0.125

            if j % 512 == 511:
                # in javascript version, these two are called when a buffer is completely processed
                self.pt_tract.handleTouches(cur_touches=self.touches[j])
                self.pt_glottis.handleTouches(cur_touches=self.touches[j])
                self.pt_glottis.finishBlock()
                self.pt_tract.finishBlock()
        return outArray
