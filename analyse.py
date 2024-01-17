from datetime import timedelta
import numpy as np
import soundfile as sf


class DetectDiscontinuity:
    def __init__(self) -> None:
        file_data = None

    def load_file(self, filename) -> bool:





def get_time_ms(frame_num: int, samples_rate: int) -> int:
    return frame_num / (samples_rate / 1000)


def format_ms(ms: float) -> timedelta:
    td = timedelta(milliseconds=ms)
    return td


def get_file_info(filename: str) -> sf._SoundFileInfo:
    return sf.info(filename)


def get_sample_rate(filename: str) -> int:
    file_info = sf.info(filename)
    return file_info.samplerate


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


def detect_discontinuities(
    filename: str, threshold: float, plot: bool = False
) -> list[list[int]]:
    try:
        file_info = sf.info(filename)
        num_channels = file_info.channels
        sample_rate = file_info.samplerate
        blocksize = sample_rate
        overlap = int(sample_rate / 1000)

        if plot:
            # Read the whole file at once
            print("Reading the whole file")
            file_data, _ = sf.read(filename)
        else:
            # Read the file in blocks
            print(f"Reading the file in blocks of: {blocksize} frames")
            file_data = sf.blocks(filename, blocksize=blocksize, overlap=overlap)

        current_start_frame = 0
        discontinuities = []

        for block in file_data:
            # Create an ndarray for each channel
            if num_channels > 1:
                samples = block.T
            else:
                samples = block.reshape(1, -1)

            abs_deriv = calc_abs_derivative(samples)
            block_discont = get_discontinuities(abs_deriv, threshold=threshold)

            for channel in range(num_channels):
                for discont in block_discont[channel]:
                    abs_frame = discont + current_start_frame
                    discontinuities.append(abs_frame)

            # Update next block start time
            current_start_frame += blocksize - overlap

        # remove duplicates and sort low to high
        discontinuities = list(set(discontinuities))
        discontinuities.sort()

        return discontinuities

    except sf.LibsndfileError:
        print(f"File ('{filename}') not found")
        return None
