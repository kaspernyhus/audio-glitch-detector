import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from utils import (
    split_channels,
    normalize_data,
    calc_abs_derivative,
    get_discontinuities,
    remove_duplicates,
)


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


if __name__ == "__main__":
    print("Detecting Discontinuities in sine waves realtime")
    open_audio_stream()
