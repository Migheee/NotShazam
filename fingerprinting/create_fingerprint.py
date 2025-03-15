import os
import librosa
import librosa.display 
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter
import time  # For measuring the execution time

# Set the log flag to True to enable the logging of the execution time
ENABLE_LOG = False

FRAME_SIZE = 2048
HOP_SIZE = 512
NEIGHBORHOOD_SIZE = 20
TIME_INTERVAL = 50
FREQUENCY_INTERVAL = 22

def log_time(func):
    '''
    Decoratore per misurare il tempo di esecuzione di una funzione
    :param func: la funzione da misurare
    :return: la funzione con il log del tempo
    '''
    def wrapper(*args, **kwargs):
        if ENABLE_LOG:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"Tempo di esecuzione di {func.__name__}: {(end_time - start_time) * 1000:.2f} ms")
        else:
            result = func(*args, **kwargs)
        return result
    return wrapper


@log_time
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

    # DB conversion of the amplitude (since the human ear perceives the loudness of a sound on a logarithmic scale)
    Y_scale = np.abs(S) ** 2  # Squared magnitude of the STFT (to get the power spectrogram)
    Y_log = librosa.power_to_db(Y_scale)

    return Y_log, sr


@log_time
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


@log_time
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


@log_time
def get_anchor_point(peaks, min_intensity=20):
    '''
    This function finds the anchor points in the spectrogram
    :param peaks: the coordinates of the peaks
    :return: the anchor points
    '''
    anchor_points = []
    
    # Pre-filtraggio dei picchi in base all'intensità minima
    peaks = [peak for peak in peaks if spectrogram[peak[0], peak[1]] > min_intensity]
    
    for i in range(len(peaks)):
        for j in range(i + 1, len(peaks)):  # From i+1 to avoid duplicates
            # Limita i confronti ai picchi che sono abbastanza vicini nel tempo e nella frequenza
            if abs(peaks[i][0] - peaks[j][0]) < TIME_INTERVAL and abs(peaks[i][1] - peaks[j][1]) < FREQUENCY_INTERVAL:
                anchor_points.append((peaks[i], peaks[j]))
                
    return anchor_points



@log_time
def get_fingerprint(anchor_points):
    '''
    This function generates the fingerprint of a song
    :param anchor_points: the anchor points
    :return: the fingerprint of the song
    '''
    fingerprint = []
    for (f1, t1), (f2, t2) in anchor_points:
        time_diff = t2 - t1
        frequency_diff = f2 - f1
        fingerprint.append((time_diff, frequency_diff))

    return fingerprint

