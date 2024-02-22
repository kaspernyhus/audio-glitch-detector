import argparse
from detectors.detector_file import DiscontinuityDetectorFile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--threshold",
        default=0.1,
        required=False,
        help="discontinuity detection threshold (>0.06)",
    )
    parser.add_argument("-f", "--filename", required=False, help="wave file to analyse")
    args = parser.parse_args()
    filename = args.filename
    threshold = args.threshold

    with DiscontinuityDetectorFile(filename, threshold) as dd:
        dd.process_file()
        dd.show_results()


if __name__ == "__main__":
    main()
