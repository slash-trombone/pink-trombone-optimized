import os
import numpy as np
import surfboard.formants as sbformants
import librosa
import librosa.display
import pyloudnorm as pyln


filepath_audio_t = './tongue/audio/'
filepath_pos_t = './tongue/pos/'
sr = 48000


def read_all(filepath):
    files = os.listdir(filepath)
    return files


def getMel():
    audio_files = read_all(filepath_audio_t)
    mel = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        cur_mel = librosa.feature.melspectrogram(audio_data, sr=sr, center=False).T[1:, :].tolist()
        mel.append(cur_mel)
    np.save("tongue_features/mel.npy", mel)


def getMfcc():
    audio_files = read_all(filepath_audio_t)
    mel = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        cur_mel = librosa.feature.mfcc(audio_data, sr=sr).tolist()
        mel.append(cur_mel)
    np.save("tongue_features/mfcc.npy", mel)


def nn_data_pre():
    pos_files = read_all(filepath_pos_t)
    audio_files = read_all(filepath_audio_t)

    # tongue position
    # [depend on sequence in dataGeneration][0]
    # center : False
    t_pos_x = []
    for file in pos_files:
        cur_pos = []
        cur_index = 1023
        pos_data = np.load(filepath_pos_t + file, allow_pickle=True).tolist()
        while cur_index + 1024 <= len(pos_data):
            cur_pos.append(pos_data[cur_index][0][0])
            cur_index += 512
        t_pos_x.append(cur_pos[1:])

    t_pos_y = []
    for file in pos_files:
        cur_pos = []
        cur_index = 1023
        pos_data = np.load(filepath_pos_t + file, allow_pickle=True).tolist()
        while cur_index + 1024 <= len(pos_data):
            cur_pos.append(pos_data[cur_index][0][1])
            cur_index += 512
        t_pos_y.append(cur_pos[1:])

    # # glottis position
    # # [depend on sequence in dataGeneration][0]
    # # center : True
    # g_pos_x = []
    # for file in pos_files:
    #     cur_pos = []
    #     cur_index = 2047
    #     pos_data = np.load(filepath_pos_t + file, allow_pickle=True).tolist()
    #     while cur_index <= len(pos_data):
    #         cur_pos.append(pos_data[cur_index - 1023][0][0])
    #         cur_index += 512
    #     g_pos_x.append(cur_pos[1:])
    #
    # g_pos_y = []
    # for file in pos_files:
    #     cur_pos = []
    #     cur_index = 2047
    #     pos_data = np.load(filepath_pos_t + file, allow_pickle=True).tolist()
    #     while cur_index <= len(pos_data):
    #         cur_pos.append(pos_data[cur_index - 1023][0][1])
    #         cur_index += 512
    #     g_pos_y.append(cur_pos[1:])

    pitch = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file)
        f0, voiced_flag, voiced_probs = librosa.pyin(audio_data, fmin=librosa.note_to_hz('C0'),
                                                     fmax=librosa.note_to_hz('C7'), sr=sr, center=False)
        pitch.append(f0[1:])

    # diameter = []
    # for file in pos_files:
    #     cur_diameter = []
    #     cur_index = 2047
    #     pos_data = np.load(filepath_pos_t + file, allow_pickle=True).tolist()
    #     while cur_index <= len(pos_data):
    #         cur_diameter.append(pos_data[cur_index - 1023][0])
    #         cur_index += 512
    #     diameter.append(cur_diameter[1:])

    loudness = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)

        stft = librosa.stft(audio_data, n_fft=2048, center=False)  # 复数矩阵
        power_spectrum = np.square(np.abs(stft))  # 求绝对值得到振幅，再取平方得到频谱
        bins = librosa.fft_frequencies(sr=sr, n_fft=2048)
        cur_loudness = librosa.perceptual_weighting(power_spectrum, bins)
        cur_loudness = librosa.db_to_amplitude(cur_loudness)
        cur_loudness = np.log(np.mean(cur_loudness, axis=0) + 1e-5).tolist()
        loudness.append(cur_loudness[1:])

    rms = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        cur_rms = librosa.feature.rms(audio_data, center=False).tolist()[0]
        rms.append(cur_rms[1:])

    py_loudness = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file)
        cur_loudness = []
        start_index = 0
        end_index = 2048
        while end_index < len(audio_data):
            cur_data = audio_data[start_index:end_index]
            meter = pyln.Meter(48000, block_size=2048 / 48000)
            loud_value = meter.integrated_loudness(cur_data)
            cur_loudness.append(loud_value)
            start_index += 512
            end_index += 512
        py_loudness.append(cur_loudness[1:])

    spectral_centroid = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        cur_sc = librosa.feature.spectral_centroid(audio_data, sr=sr, center=False).tolist()[0]
        spectral_centroid.append(cur_sc[1:])

    spectral_bandwidth = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        cur_sb = librosa.feature.spectral_bandwidth(audio_data, sr=sr, center=False).tolist()[0]
        spectral_bandwidth.append(cur_sb[1:])

    spectral_rolloff = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        cur_sb = librosa.feature.spectral_rolloff(audio_data, sr=sr, center=False).tolist()[0]
        spectral_rolloff.append(cur_sb[1:])

    spectral_contrast = []
    for file in audio_files:
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        cur_sb = librosa.feature.spectral_contrast(audio_data, sr=sr, center=False).tolist()[0]
        spectral_contrast.append(cur_sb[1:])

    f1, f2, f3, f4 = [], [], [], []
    for file in audio_files:
        # zeros = np.array([0 for i in range(1024)])
        audio_data = np.load(filepath_audio_t + file, allow_pickle=True)
        # audio_data = np.concatenate((zeros, audio_data, zeros), axis=0)
        cur_f1, cur_f2, cur_f3, cur_f4 = [], [], [], []

        start_index = 0
        end_index = 2048

        while end_index < audio_data.shape[0]:
            cur_data = audio_data[start_index: end_index]
            formants = sbformants.get_formants(cur_data, sr)

            cur_f1.append(formants['f1'])
            cur_f2.append(formants['f2'])
            cur_f3.append(formants['f3'])
            cur_f4.append(formants['f4'])

            start_index += 512
            end_index += 512

        f1.append(cur_f1[1:])
        f2.append(cur_f2[1:])
        f3.append(cur_f3[1:])
        f4.append(cur_f4[1:])

    np.save("tongue_features/t_pos_x.npy", t_pos_x)
    np.save("tongue_features/t_pos_y.npy", t_pos_y)
    np.save("tongue_features/f1.npy", f1)
    np.save("tongue_features/f2.npy", f2)
    np.save("tongue_features/f3.npy", f3)
    np.save("tongue_features/f4.npy", f4)
    np.save("tongue_features/ff.npy", pitch)
    np.save("tongue_features/rms.npy", rms)
    np.save("tongue_features/pyloud.npy", py_loudness)
    np.save("tongue_features/loudness.npy", loudness)
    np.save("tongue_features/spectral_rolloff.npy", spectral_rolloff)
    np.save("tongue_features/spectral_centroid.npy", spectral_centroid)
    np.save("tongue_features/spectral_contrast.npy", spectral_contrast)
    np.save("tongue_features/spectral_bandwidth.npy", spectral_bandwidth)

