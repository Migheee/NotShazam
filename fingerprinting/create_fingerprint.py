
import os
import librosa
import librosa.display 
import numpy as np
import hashlib
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter
from scipy.spatial import KDTree
import time  # For measuring the execution time

# Set the log flag to True to enable the logging of the execution time
ENABLE_LOG = True

FRAME_SIZE = 2048
HOP_SIZE = 512
NEIGHBORHOOD_SIZE = 20
TIME_INTERVAL = 32
FREQUENCY_INTERVAL = 12

def log_time(func):
    '''
    This function is a decorator that logs the execution time of a function
    :param func: the function to be logged
    :return: the wrapper function
    '''
    def wrapper(*args, **kwargs):
        if ENABLE_LOG:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"Execution Time {func.__name__}: {(end_time - start_time) * 1000:.2f} ms")
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
    song, sr = librosa.load(file_path)
    S = np.abs(librosa.stft(song, n_fft=FRAME_SIZE, hop_length=HOP_SIZE)) ** 2
    return librosa.power_to_db(S)

@log_time
def plot_spectrogram(s, sr):
    '''
    This function plots the spectrogram of a song
    :param spectrogram: the spectrogram of the song
    :param sr: the sampling rate of the song
    '''
    plt.figure(figsize=(12, 8))
    librosa.display.specshow(spectrogram, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('òSpectrogram')
    plt.show()


@log_time
def get_peaks(spectrogram):
    '''
    This function finds the peaks in the spectrogram
    :param spectrogram: the spectrogram of the song
    :return: the coordinates of the peaks
    '''
    # Find the local maxima in the spectrogram, using a neighborhood of a given size (20x20)
    print(type(spectrogram))
    filtered_spectrogram = maximum_filter(spectrogram, size=NEIGHBORHOOD_SIZE)
    # Find the peaks by comparing the filtered spectrogram with the original one, by element-wise comparison and creating a boolean matrix
    peaks = (spectrogram == filtered_spectrogram)
    # Get the coordinates of the peaks, by finding the indices of the True values in the boolean matrix
    peak_coords = np.argwhere(peaks)
    return peak_coords


@log_time
def get_anchor_points(spectrogram, peaks, min_intensity=20):
    # Filtro picchi per intensità minima
    peaks = np.array([p for p in peaks if spectrogram[p[0], p[1]] > min_intensity])
    
    if len(peaks) == 0:
        return []

    # Creazione del KDTree
    tree = KDTree(peaks)

    anchor_points = []
    for peak in peaks:
        # Trova i vicini nel range specificato
        indices = tree.query_ball_point(peak, r=max(TIME_INTERVAL, FREQUENCY_INTERVAL))
        
        for idx in indices:
            neighbor = peaks[idx]
            # Controlla che il vicino rispetti i vincoli di distanza
            if 0 < abs(peak[0] - neighbor[0]) < TIME_INTERVAL and 0 < abs(peak[1] - neighbor[1]) < FREQUENCY_INTERVAL:
                anchor_points.append((tuple(peak), tuple(neighbor)))

    return anchor_points


@log_time
def get_fingerprint(anchor_points):
    '''
    Generates a hashed fingerprint for the audio file.
    :param anchor_points: List of selected anchor points.
    :return: List of hashed fingerprints for the song.
    '''
    fingerprint_hashes = []
    for (f1, t1), (f2, t2) in anchor_points:
        # Calculate the time and frequency differences
        time_diff = int(t2 - t1)  # Convert numpy int64 to regular int
        frequency_diff = int(f2 - f1)  # Convert numpy int64 to regular int

        # Create a unique hash using the differences
        data = f"{f1}-{t1}-{f2}-{t2}-{time_diff}-{frequency_diff}".encode()
        # Use SHA-1 hash and get a fixed-length hash string (first 10 chars of SHA-1 hash)
        combined_hash = hashlib.sha1(data).hexdigest()[:10]
        fingerprint_hashes.append(combined_hash)

    return fingerprint_hashes

@log_time
def process_audio(file_path):
    spectrogram = get_spectrogram(file_path)

    peaks = get_peaks(spectrogram)
    anchor_points = get_anchor_points(spectrogram, peaks)
    fingerprint = get_fingerprint(anchor_points)
    print(len(fingerprint))




# Esempio di utilizzo
if __name__ == "__main__":
    file_path = "songs/Glue.wav"
    process_audio(file_path)

