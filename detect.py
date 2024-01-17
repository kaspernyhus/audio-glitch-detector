import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import sys
import argparse
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


def normalize_data(data):
    # Convert data to float
    data = data.astype(float)
    # Find the maximum absolute value in the data
    max_val = np.max(np.abs(data))
    # Normalize data to floats between -1.0 and 1.0
    data /= max_val
    return data


def plot_result(samples: np.ndarray, abs_deriv: np.ndarray):
    num_channels = samples.shape[0]

    fig, axs = plt.subplots(num_channels * 2, 1, sharex=True)
    for channel in range(num_channels):
        axs[channel].plot(samples[channel], label="input wave")
        axs[channel + num_channels].plot(
            abs_deriv[channel], label="absolut of derivative"
        )
        axs[channel].set_ylim([-1.2, 1.2])
        axs[channel + num_channels].set_ylim([0, 2])

    plt.show()


def split_channels(samples: np.ndarray, channels: int) -> np.ndarray:
    return np.vstack([samples[i::channels] for i in range(channels)])


def get_time_ms(frame_num: int, samples_rate: int) -> int:
    return frame_num / (samples_rate / 1000)


def format_ms(ms: float) -> timedelta:
    td = timedelta(milliseconds=ms)
    return td


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="wave file to analyse")
    parser.add_argument(
        "-t",
        "--threshold",
        default=0.1,
        required=False,
        help="threshold for discontinuity",
    )
    args = parser.parse_args()

    try:
        print("--------------------------------------------")
        file_info = sf.info(args.filename)
        print(file_info)

        num_channels = file_info.channels
        sample_rate = file_info.samplerate

        current_start_frame = 0

        blocksize = sample_rate
        overlap = int(sample_rate / 1000)

        print(f"Blocksize: {blocksize}, overlap: {overlap}")

        discontinuities = []

        for block in sf.blocks(
            args.filename, blocksize=blocksize, overlap=overlap, start=0
        ):
            # Create an ndarray for each channel
            if num_channels > 1:
                samples = block.T
            else:
                samples = block.reshape(1, -1)

            abs_deriv = calc_abs_derivative(samples)
            block_discont = get_discontinuities(abs_deriv, threshold=args.threshold)

            for channel in range(num_channels):
                for discont in block_discont[channel]:
                    abs_frame = discont + current_start_frame
                    discontinuities.append(abs_frame)

            # Update next block start time
            current_start_frame += blocksize - overlap

        # remove duplicates and sort low to high
        discontinuities = list(set(discontinuities))
        discontinuities.sort()

        print("--------------------------------------------")
        print("Number of discontinuities detected: ", len(discontinuities))
        for disc in discontinuities:
            ms = get_time_ms(disc, sample_rate)
            print(format_ms(ms))
        print("--------------------------------------------")

    except sf.LibsndfileError:
        print(f"File ('{args.filename}') not found")
        sys.exit(-1)


if __name__ == "__main__":
    main()
