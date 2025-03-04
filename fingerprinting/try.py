'''
Author: Michele Castenedoli
Date: 04/03/2025
Generates the spectrogram of a song
'''

import os
import librosa
import librosa.display 
import numpy as np
import matplotlib.pyplot as plt


FRAME_SIZE = 2048
HOP_SIZE = 512

def get_spectrogram(file_path):
    # Load song
    song, sr = librosa.load(file_path)

    # Execute the STFT
    S = librosa.stft(song, n_fft=FRAME_SIZE, hop_length=HOP_SIZE)

    #DB conversion of the amplitude (since the human ear perceives the loudness of a sound on a logarithmic scale)
    Y_scale = np.abs(S) ** 2  #Squared magnitude of the STFT (to get the power spectogram)
    Y_log = librosa.power_to_db(Y_scale)


    # Show the spectrogram
    plt.figure(figsize=(25, 10))
    librosa.display.specshow(
        Y_log,
        sr=sr,
        hop_length=HOP_SIZE,
        x_axis='time',  
        y_axis='log'
    )
    plt.colorbar(format="%+2.f dB")
    plt.title("Spettrogramma STFT")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Frequenza (Hz)")
    plt.show()  # Show the plot

get_spectrogram("songs\\Soulmate.wav")
