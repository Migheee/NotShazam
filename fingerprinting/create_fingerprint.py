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
    # Load song
    song, sr = librosa.load(file_path)

    # Execute the STFT
    S = librosa.stft(song, n_fft=FRAME_SIZE, hop_length=HOP_SIZE)

    # DB conversion of the amplitude (since the human ear perceives the loudness of a sound on a logarithmic scale)
    Y_scale = np.abs(S) ** 2  # Squared magnitude of the STFT (to get the power spectrogram)
    Y_log = librosa.power_to_db(Y_scale)

    return Y_log, sr


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
def filter_peaks_by_intensity(spectrogram, peaks, percentile=85):
    '''
    Filters peaks based on intensity threshold (percentile-based).
    :param spectrogram: Spectrogram of the song
    :param peaks: Peak coordinates
    :param percentile: Intensity percentile threshold
    :return: Filtered peak coordinates
    '''
    intensities = [spectrogram[p[0], p[1]] for p in peaks]
    threshold = np.percentile(intensities, percentile)
    return [p for p in peaks if spectrogram[p[0], p[1]] >= threshold]



@log_time
def get_anchor_points(peaks, spectrogram, window_size=32):
    '''
    This function finds the anchor points in the spectrogram
    :param peaks: the coordinates of the peaks
    :param spectrogram: the spectrogram of the song
    :param window_size: the size of the window
    :return: the anchor points
    '''
    anchor_points = []
    sorted_peaks = sorted(peaks, key=lambda x: x[1])  # Order by time

    for i in range(0, len(sorted_peaks), window_size):
        window_peaks = sorted_peaks[i:i+window_size] # Get the peaks in the window
        if window_peaks:
            best_peak = max(window_peaks, key=lambda p: spectrogram[p[0], p[1]]) # Get the peak with the highest intensity
            anchor_points.append(best_peak)

    return anchor_points



@log_time
def generate_fingerprint(anchor_points):
    """
    Generates a fingerprint for the audio file.
    :param anchor_points: List of selected anchor points.
    :return: List of 32-bit hashes representing the fingerprint.
    """
    fingerprint = []
    for i in range(len(anchor_points)):
        for j in range(i + 1, len(anchor_points)):  # Avoid duplicate pairs
            f1, t1 = anchor_points[i]
            f2, t2 = anchor_points[j]

            # Compute time and frequency differences
            time_diff = int(t2 - t1)
            frequency_diff = int(f2 - f1)

            # Generate a robust hash
            combined_hash = hash_fingerprint(f1, t1, f2, t2)
            fingerprint.append(combined_hash)

    return fingerprint
    

@log_time
def hash_fingerprint(f1, t1, f2, t2):
    """
    Generates a robust hash for the fingerprint.
    :param f1, t1, f2, t2: Frequency and time values of anchor points.
    :return: SHA-1 hash of the fingerprint.
    """
    data = f"{f1}-{t1}-{f2}-{t2}".encode()
    return hashlib.sha1(data).hexdigest()[:10]  # Take only the first 10 characters
