import sys
import argparse
from detectors.detect_discontinuity_file import DetectDiscontinuitiesFile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="wave file to analyse")
    parser.add_argument(
        "-t",
        "--threshold",
        default=0.1,
        required=False,
        help="discontinuity detection threshold > 0.06",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="file",
        required=False,
        help="mode: file or stream",
    )
    parser.add_argument("-f", "--filename", help="wave file to analyse")

    args = parser.parse_args()

    mode = args.mode
    filename = args.filename
    threshold = args.threshold

    if mode == "file":
        with DetectDiscontinuitiesFile(filename, threshold) as dd:
            dd.process_file()
            dd.show_results()
    else:
        pass


if __name__ == "__main__":
    main()
