'''
Author: Michele Castenedoli
Creation Date: 04/03/2025
Last Update: 15/03/2025
Generates the spectrogram of a song, finds the peaks in the spectrogram
'''

import os
import librosa
import librosa.display 
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter


FRAME_SIZE = 2048
HOP_SIZE = 512
NEIGHBORHOOD_SIZE = 20

def get_spectrogram(file_path):
    '''
    This function generates the spectrogram of a song
    :param file_path: path to the song
    :return: the spectrogram and the sampling rate of the song
    '''

    # Load song
    song, sr = librosa.load(file_path)

    # Execute the STFT
    S = librosa.stft(song, n_fft=FRAME_SIZE, hop_length=HOP_SIZE)

    #DB conversion of the amplitude (since the human ear perceives the loudness of a sound on a logarithmic scale)
    Y_scale = np.abs(S) ** 2  #Squared magnitude of the STFT (to get the power spectogram)
    Y_log = librosa.power_to_db(Y_scale)

    return Y_log, sr

def plot_spectogram(spectogram, sr):
    '''
    This function plots the spectrogram of a song
    :param spectogram: the spectrogram of the song
    :param sr: the sampling rate of the song
    '''

    plt.figure(figsize=(12, 8))
    librosa.display.specshow(spectogram, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.show()


def get_peaks(spectrogram):
    '''
    This function finds the peaks in the spectrogram
    :param spectrogram: the spectrogram of the song
    :return: the coordinates of the peaks
    '''

    # Find the local maxima in the spectrogram, using a neighborhood of a given size (20x20)
    filtered_spectrogram = maximum_filter(spectrogram, size=NEIGHBORHOOD_SIZE)
    # Find the peaks by comparing the filtered spectrogram with the original one, by element-wise comparison and creating a boolean matrix
    peaks = (spectrogram == filtered_spectrogram)
    # Get the coordinates of the peaks, by finding the indices of the True values in the boolean matrix
    peak_coords = np.argwhere(peaks)
    return peak_coords



spectrogram, sr = get_spectrogram("songs\\Soulmate.wav")
plot_spectogram(spectrogram, sr)


