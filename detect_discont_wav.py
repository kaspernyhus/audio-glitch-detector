import numpy as np
import matplotlib.pyplot as plt
import wave
import sys
import argparse


def detect_discont(wave):
    # differentiation
    filter = [-1, 1]
    dif = np.convolve(wave, filter)
    absdif = np.abs(dif)
    return absdif


def count_discont(absdif, threshold=0.5):
    # count discontinuities
    count = 0
    for i in absdif[1:-1]:
        if i > threshold:
            count += 1
    return count


def normalize_data(data):
    # Convert data to float
    data = data.astype(float)
    # Find the maximum absolute value in the data
    max_val = np.max(np.abs(data))
    # Normalize data to floats between -1.0 and 1.0
    data /= max_val
    return data


def plot_wave(wave, absdif):
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(wave, label="input wave")
    ax2.plot(absdif, label="absolut of derivative")
    plt.show()


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
            data = wf.readframes(-1)
            data = np.frombuffer(data, dtype=np.int16)
            data = normalize_data(data)
            absdif = detect_discont(data)
            count = count_discont(absdif, threshold=args.threshold)
    except FileNotFoundError:
        print(f"File ('{args.filename}') not found")
        sys.exit(-1)

    print("Number of discontinuities detected: ", count)

    if args.plot:
        plot_wave(data, absdif)


if __name__ == "__main__":
    main()
