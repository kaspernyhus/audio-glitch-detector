import argparse
import signal
from time import sleep
from threading import Event
from detectors.detector_stream import DiscontinuityDetectorStream
from utils.audio_format import AudioFormat, AudioBits
from utils.rich_output import RichOutput

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
        "-d",
        "--device_id",
        type=int,
        required=False,
        default=None,
        help="Sound device ID. Use list_devices.py to list available devices",
    )
    parser.add_argument(
        "-s", "--save_blocks", required=False, default=False, help="Save erroneous audio blocks as .wav files"
    )
    args = parser.parse_args()
    device_id = args.device_id
    threshold = args.threshold
    save_blocks = args.save_blocks

    detect = DiscontinuityDetectorStream(
        AudioFormat(FORMAT=AudioBits.FORMAT_32LE, CHANNELS=2, RATE=48000, CHUNK=1024),
        device_id=device_id,
        save_blocks=save_blocks,
        threshold=threshold,
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
