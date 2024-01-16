import numpy as np
import matplotlib.pyplot as plt
import wave
import sys
import argparse


def calc_abs_derivative(samples: np.ndarray) -> np.ndarray:
    """Calculating the absolute value of the first derivative of the signal"""
    num_channels = samples.shape[0]
    signal_deriv = np.zeros(samples.shape)

    filter = [-1, 1]

    for channel in range(num_channels):
        signal_deriv[channel] = np.abs(np.convolve(samples[channel], filter))[:-1]

    return signal_deriv


def count_discontinuities(abs_deriv: np.ndarray, threshold=0.5) -> list[int]:
    """Count the number of discontinuities in the signal above a threshold"""
    num_channels = abs_deriv.shape[0]
    counts = [0] * num_channels

    for channel in range(num_channels):
        for sample in abs_deriv[channel][1:-1]:
            if sample > threshold:
                counts[channel] += 1

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="wave file to analyse")
    parser.add_argument(
        "-t",
        "--threshold",
        default=0.15,
        required=False,
        help="threshold for discontinuity",
    )
    parser.add_argument(
        "-p",
        "--plot",
        default=True,
        required=False,
        help="plot the wave and the derivative",
    )
    args = parser.parse_args()

    try:
        with wave.open(args.filename, "rb") as wf:
            channels = wf.getnchannels()
            print("channels: ", channels)

            samples = wf.readframes(-1)
            samples = np.frombuffer(samples, dtype=np.int16)
            samples = normalize_data(samples)
            samples = split_channels(samples, channels)

            abs_deriv = calc_abs_derivative(samples)
            count = count_discontinuities(abs_deriv, threshold=args.threshold)
            print("Number of discontinuities detected: ", count)

            if args.plot:
                plot_result(samples, abs_deriv)

    except FileNotFoundError:
        print(f"File ('{args.filename}') not found")
        sys.exit(-1)


if __name__ == "__main__":
    main()
