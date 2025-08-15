import numpy as np
from datetime import timedelta


def count_discontinuities(abs_deriv: np.ndarray, threshold=0.5) -> list[list[int]]:
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


def get_time_ms(frame_num: int, samples_rate: int) -> int:
    """Convert frame number to milliseconds"""
    return frame_num / (samples_rate / 1000)


def format_ms(ms: float) -> timedelta:
    """Convert milliseconds to a timedelta object"""
    td = timedelta(milliseconds=ms)
    return td
