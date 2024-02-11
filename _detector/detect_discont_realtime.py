import pyaudio
import argparse
import numpy as np
import matplotlib.pyplot as plt


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


def normalize_data(data):
    # Convert data to float
    data = data.astype(float)
    # Find the maximum absolute value in the data
    max_val = np.max(np.abs(data))
    # Normalize data to floats between -1.0 and 1.0
    data /= max_val
    return data


def split_channels(samples: np.ndarray, channels: int) -> np.ndarray:
    return np.vstack([samples[i::channels] for i in range(channels)])


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


def process_audio_data(data):
    # Convert raw bytes to NumPy array
    block = np.frombuffer(data, dtype=np.int16)
    samples = split_channels(block, 2)
    samples = normalize_data(samples)

    abs_deriv = calc_abs_derivative(samples)
    block_discont = get_discontinuities(abs_deriv, threshold=0.2)

    discontinuities = []
    for channel in range(samples.shape[0]):
        discontinuities.extend(block_discont[channel])

    discont = remove_duplicates(discontinuities)
    num_discont = len(discont)
    return num_discont


def open_audio_stream():
    # Constants
    FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
    CHANNELS = 2  # Mono audio
    RATE = 48000  # Sample rate
    CHUNK = 1024  # Block size

    p = pyaudio.PyAudio()

    input_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    total_discontinuities = 0

    try:
        for _ in range(100):
            input_data = input_stream.read(CHUNK)

        while True:
            input_data = input_stream.read(CHUNK)
            discontinuities = process_audio_data(input_data)
            if discontinuities > 0:
                total_discontinuities += discontinuities
                print(f"Discontinuities detected: {total_discontinuities}")

    except KeyboardInterrupt:
        # Stop and close the stream
        input_stream.stop_stream()
        input_stream.close()
        p.terminate()


def main():
    print("Detecting Discontinuities in sine waves realtime")

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    open_audio_stream()


if __name__ == "__main__":
    main()
