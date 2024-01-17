import sys
import argparse
from _detector.detect_discontinuities import DetectDiscontinuities


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

    filename = args.filename
    threshold = args.threshold

    with DetectDiscontinuities(filename, threshold) as dd:
        dd.process_file()
        dd.show_results()


if __name__ == "__main__":
    main()
