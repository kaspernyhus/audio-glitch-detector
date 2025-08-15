import numpy as np


def calc_abs_derivative(samples: np.ndarray) -> np.ndarray:
    """Calculating the absolute value of the first derivative of the signal"""
    num_channels = samples.shape[0]
    signal_deriv = np.zeros(samples.shape)
    filter = [-1, 1]
    for channel in range(num_channels):
        signal_deriv[channel] = np.abs(np.convolve(samples[channel], filter))[:-1]
    return signal_deriv


def normalize_data(data):
    """Normalize data to floats between -1.0 and 1.0"""
    max_val = np.max(np.abs(data))
    if max_val == 0:
        return data  # Or np.zeros_like(data) if you want all zero output

    data = data / max_val
    return data


def convert_to_float(data: np.ndarray) -> np.ndarray:
    """Convert integer data to floats between -1.0 and 1.0"""
    return data.astype(float) / np.iinfo(data.dtype).max


def split_channels(samples: np.ndarray, channels: int) -> np.ndarray:
    """Split interleaved samples into separate channels"""
    return np.vstack([samples[i::channels] for i in range(channels)])


def get_samples_from_block(block: bytes, channels: int, bit_depth: int) -> np.ndarray:
    """Convert raw bytes to NumPy array and split channels if necessary. Normalize data to floats between -1.0 and 1.0."""
    if bit_depth == 16:
        bit_depth = np.int16
    elif bit_depth == 32:
        bit_depth = np.int32

    return np.frombuffer(block, dtype=bit_depth)
