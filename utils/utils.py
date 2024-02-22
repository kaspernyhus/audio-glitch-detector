import numpy as np
from datetime import timedelta


def calc_abs_derivative(samples: np.ndarray) -> np.ndarray:
    """Calculating the absolute value of the first derivative of the signal"""
    num_channels = samples.shape[0]
    signal_deriv = np.zeros(samples.shape)
    filter = [-1, 1]
    for channel in range(num_channels):
        signal_deriv[channel] = np.abs(np.convolve(samples[channel], filter))[:-1]
    return signal_deriv


def get_discontinuities(abs_deriv: np.ndarray, threshold=0.5) -> list[list[int]]:
    """Return a list of sample numbers where a discontinuity in the signal is detected"""
    num_channels = abs_deriv.shape[0]
    counts = [[]] * num_channels
    for channel in range(num_channels):
        for index, sample in enumerate(abs_deriv[channel][1:-1]):
            if sample > threshold:
                counts[channel].append(index + 1)
    return counts


def remove_duplicates(discontinuities: list[int], window=10):
    """remove duplicates within a window of samples"""
    if discontinuities:
        discont = list(set(discontinuities))
        discont.sort()
        discont_cleaned = [discont[0]]
        for value in discont[1:]:
            if value - discont_cleaned[-1] >= window:
                discont_cleaned.append(value)
        return discont_cleaned
    else:
        return []


def normalize_data(data):
    """Normalize data to floats between -1.0 and 1.0"""
    # Find the maximum absolute value in the data
    max_val = np.max(np.abs(data))
    # Normalize data to floats between -1.0 and 1.0
    data /= max_val
    return data


def get_samples_from_block(block: bytes, channels: int, bit_depth: int) -> np.ndarray:
    """Convert raw bytes to NumPy array and split channels if necessary. Normalize data to floats between -1.0 and 1.0."""
    if bit_depth == 16:
        bit_depth = np.int16
    elif bit_depth == 32:
        bit_depth = np.int32

    return np.frombuffer(block, dtype=bit_depth)


def convert_to_float(data: np.ndarray) -> np.ndarray:
    """Convert integer data to floats between -1.0 and 1.0"""
    return data.astype(float) / np.iinfo(data.dtype).max


def split_channels(samples: np.ndarray, channels: int) -> np.ndarray:
    """Split interleaved samples into separate channels"""
    return np.vstack([samples[i::channels] for i in range(channels)])


def get_time_ms(frame_num: int, samples_rate: int) -> int:
    """Convert frame number to milliseconds"""
    return frame_num / (samples_rate / 1000)


def format_ms(ms: float) -> timedelta:
    """Convert milliseconds to a timedelta object"""
    td = timedelta(milliseconds=ms)
    return td
