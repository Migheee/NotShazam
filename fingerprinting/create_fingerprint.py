import os
import librosa
import librosa.display 
import numpy as np
import xxhash
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
    This function is a decorator that logs the execution time of a function.
    :param func: The function whose execution time needs to be logged.
    :return: The wrapper function that logs the execution time and calls the original function.
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
    This function generates the spectrogram of an audio file.
    :param file_path: Path to the audio file.
    :return: The spectrogram of the song and the sampling rate.
    '''
    song, sr = librosa.load(file_path)
    S = np.abs(librosa.stft(song, n_fft=FRAME_SIZE, hop_length=HOP_SIZE)) ** 2
    return librosa.power_to_db(S)


@log_time
def plot_spectrogram(spectrogram, sr):
    '''
    This function plots the spectrogram of the song.
    :param spectrogram: The spectrogram of the song.
    :param sr: The sampling rate of the song.
    '''
    plt.figure(figsize=(12, 8))
    librosa.display.specshow(spectrogram, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.show()


@log_time
def get_peaks(spectrogram):
    '''
    This function finds the peaks in the spectrogram.
    :param spectrogram: The spectrogram of the song.
    :return: The coordinates of the peaks in the spectrogram.
    '''
    # Find the local maxima in the spectrogram, using a neighborhood of a given size (20x20)
    filtered_spectrogram = maximum_filter(spectrogram, size=NEIGHBORHOOD_SIZE)
    # Find the peaks by comparing the filtered spectrogram with the original one
    peaks = (spectrogram == filtered_spectrogram)
    # Get the coordinates of the peaks
    peak_coords = np.argwhere(peaks)
    return peak_coords


@log_time
def get_anchor_points(spectrogram, peaks, min_intensity=20):
    '''
    This function generates anchor points based on the spectrogram peaks.
    :param spectrogram: The spectrogram of the song.
    :param peaks: The coordinates of the peaks in the spectrogram.
    :param min_intensity: Minimum intensity threshold for peaks to be considered.
    :return: List of anchor points that meet the intensity and distance criteria.
    '''
    # Filter peaks based on minimum intensity threshold
    peaks = np.array([p for p in peaks if spectrogram[p[0], p[1]] > min_intensity])
    
    if len(peaks) == 0:
        return []

    # Create KDTree for efficient nearest neighbor search
    tree = KDTree(peaks)

    anchor_points = []
    for peak in peaks:
        # Find neighbors within the specified radius
        indices = tree.query_ball_point(peak, r=max(TIME_INTERVAL, FREQUENCY_INTERVAL))
        
        for idx in indices:
            neighbor = peaks[idx]
            # Check that the neighbor respects the distance constraints
            if 0 < abs(peak[0] - neighbor[0]) < TIME_INTERVAL and 0 < abs(peak[1] - neighbor[1]) < FREQUENCY_INTERVAL:
                anchor_points.append((tuple(peak), tuple(neighbor)))

    return anchor_points


@log_time
def get_fingerprint(anchor_points):
    '''
    This function generates a hashed fingerprint for the song using the anchor points.
    :param anchor_points: List of selected anchor points.
    :return: List of hashed fingerprints for the song.
    '''
    fingerprint_hashes = []
    for (f1, t1), (f2, t2) in anchor_points:
        # Calculate the time and frequency differences
        time_diff = int(t2 - t1)  # Convert numpy int64 to regular int
        frequency_diff = int(f2 - f1)  # Convert numpy int64 to regular int

        # Create a unique hash using the differences and xxhash for better performance
        data = f"{f1}-{t1}-{f2}-{t2}-{time_diff}-{frequency_diff}".encode()
        # Use xxhash for fast hashing and get a fixed-length hash
        combined_hash = xxhash.xxh64(data).hexdigest()[:10]
        fingerprint_hashes.append(combined_hash)

    return fingerprint_hashes


@log_time
def process_audio(file_path):
    '''
    This function processes the audio file by generating its spectrogram, finding peaks, generating anchor points, 
    and creating the fingerprint.
    :param file_path: Path to the audio file.
    '''
    spectrogram = get_spectrogram(file_path)

    peaks = get_peaks(spectrogram)
    anchor_points = get_anchor_points(spectrogram, peaks)
    fingerprint = get_fingerprint(anchor_points)
    print(len(fingerprint))


# Example usage
if __name__ == "__main__":
    file_path = "songs/Glue.wav"
    process_audio(file_path)
