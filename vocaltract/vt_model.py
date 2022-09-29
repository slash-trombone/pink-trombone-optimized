from vocaltract import audio_system, glottis, tract
import json
import numpy as np
# import torch
# import scipy.io.wavfile as wavf


# read the output of biquadFilter
def vocal_tract(positions, length):
    # filter_input = None
    # filename_1 = 'params/input_1.json'
    # with open(filename_1, encoding='utf8') as load_f:
    #     filter_input = json.load(load_f)[0]['input_1']

    # positions = []
    # # boolean values
    # updates = []
    # filename_2 = 'params/0.json'
    # with open(filename_2, encoding='utf8') as load_f:
    #     param_files = json.load(load_f)
    #     for param_file in param_files:
    #         # updates.append(param_file['updateAmplitudes'])
    #         touches = param_file['touches']
    #         cur_touches = []
    #         if len(touches) == 0:
    #             positions.append([])
    #         else:
    #             for touch in touches:
    #                 cur_touches.append([touch['x'], touch['y'], touch['fricative_intensity']])
    #             positions.append(cur_touches)

    my_glottis = glottis.Glottis()
    my_tract = tract.Tract(my_glottis)
    my_audio_system = audio_system.AudioSystem(my_glottis, my_tract, positions)
    output = my_audio_system.startSound(length)

    # o_waveFile(output)
    return output


def o_waveFile(inputData):
    waveData = np.array(inputData)
    waveData = np.iinfo(np.int16).max * waveData
    fs = 48000
    out_f = 'loudness.wav'
    wavf.write(out_f, fs, waveData.astype(np.int16))


# vocal_tract()
# my_glottis = glottis.Glottis()
# my_tract = tongue.Tract(my_glottis)
# my_audio_system = audio_system.AudioSystem(my_glottis, my_tract, positions)
# output = my_audio_system.startSound()




