import sys
import argparse
from analyse import (
    get_file_info,
    detect_discontinuities,
    file_info,
    get_time_ms,
    format_ms,
)


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
    parser.add_argument(
        "-p",
        "--plot",
        default=False,
        required=False,
        help="plot the wave and the derivative",
    )
    args = parser.parse_args()

    file_info = get_file_info(args.filename)
    print(file_info)

    discontinuities = detect_discontinuities(
        args.filename, threshold=args.threshold, plot=args.plot
    )

    print("--------------------------------------------")
    print("Number of discontinuities detected: ", len(discontinuities))
    for disc in discontinuities:
        ms = get_time_ms(disc, file_info.sample_rate)
        print(format_ms(ms))
    print("--------------------------------------------")


if __name__ == "__main__":
    main()
