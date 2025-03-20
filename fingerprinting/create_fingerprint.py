
import os
import librosa
import librosa.display 
import numpy as np
import hashlib
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
    filtered_spectrogram = maximum_filter(spectrogram, size=NEIGHBORHOOD_SIZE)
    # Find the peaks by comparing the filtered spectrogram with the original one, by element-wise comparison and creating a boolean matrix
    peaks = (spectrogram == filtered_spectrogram)
    # Get the coordinates of the peaks, by finding the indices of the True values in the boolean matrix
    peak_coords = np.argwhere(peaks)
    return peak_coords


@log_time
def get_anchor_points(spectrogram, peaks, min_intensity=20):
    '''
    This function finds the anchor points in the spectrogram
    :param peaks: the coordinates of the peaks
    :return: the anchor points
    '''
    anchor_points = []
    
    # Pre-filter the peaks by intensity
    peaks = [peak for peak in peaks if spectrogram[peak[0], peak[1]] > min_intensity]
    
    for i in range(len(peaks)):
        for j in range(i + 1, len(peaks)):  # From i+1 to avoid duplicates
            # Check if the peaks are close in time and frequency
            if abs(peaks[i][0] - peaks[j][0]) < TIME_INTERVAL and abs(peaks[i][1] - peaks[j][1]) < FREQUENCY_INTERVAL:
                anchor_points.append((peaks[i], peaks[j]))
                
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


#Example usage
file_path = "songs/Glue.wav"
spectrogram, sr = get_spectrogram(file_path)
plot_spectrogram(spectrogram, sr)
peaks = get_peaks(spectrogram)
anchor_points = get_anchor_points(spectrogram, peaks)
fingerprint_hashes = get_fingerprint(anchor_points)
print(fingerprint_hashes)


