import argparse
import signal
from time import sleep
from threading import Event

from discontinuity_detector.detectors.detector_stream import DiscontinuityDetectorStream
from discontinuity_detector.detectors.detector_file import DiscontinuityDetectorFile
from discontinuity_detector.utils.audio_format import AudioFormat, AudioBits
from discontinuity_detector.utils.rich_output import RichOutput
from discontinuity_detector.utils.audio_devices import list_audio_devices



exit_event = Event()
count = 0


def signal_handler(sig, frame):
    exit_event.set()


def main():
    signal.signal(signal.SIGINT, signal_handler)

    def count_discontinuities(new_count: int):
        global count
        count += new_count
        rich.log(f"Discontinuity detected. Total {count}")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--threshold",
        default=0.1,
        required=False,
        help="discontinuity detection threshold (>0.06)",
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        required=False,
        default=640,
        help="Number of samples to process",
    )
    parser.add_argument(
        "-s",
        "--save_blocks",
        required=False,
        default=False,
        help="Save erroneous audio blocks as .wav files"
    )
    parser.add_argument(
        "-f", 
        "--filename", 
        required=False, 
        help="wave file to analyse"
    )
    
    args = parser.parse_args()
    
    try:
        threshold = float(args.threshold)
    except ValueError:
        print("Threshold must be a number")
        exit(1)

    save_blocks = args.save_blocks
    chunk_size = args.chunk_size
    filename = args.filename
    
    if filename:
        stream_mode = False
    else:
        stream_mode = True

    if not stream_mode:
        with DiscontinuityDetectorFile(filename, threshold) as dd:
            dd.process_file()
            dd.show_results()
    else:
        print("\nSelect audio device")
        list_audio_devices()
        device = input("Device ID: ")
        try:
            device_id = int(device)
        except ValueError:
            print("Invalid device id")
            exit(1)


        detect = DiscontinuityDetectorStream(
            AudioFormat(FORMAT=AudioBits.FORMAT_32LE, CHANNELS=2, RATE=48000, CHUNK=chunk_size),
            device_id=device_id,
            save_blocks=save_blocks,
            detection_threshold=threshold,
        )

        rich = RichOutput()
        rich.header("Audio Discontinuity Detector")

        t = detect.open(count_discontinuities=count_discontinuities, exit_event=exit_event)

        rich.live_output_start(exit_event=exit_event, get_meter_data=detect.get_meter_data)

        detect.start()
        rich.log("Audio processing started")
        sleep(0.1)

        t.join()

        rich.log("Audio processing stopped")
        rich.log(f"Total discontinuities detected: {count} in {rich.get_elapsed_time()}", style="bold red")


if __name__ == "__main__":
    main()
