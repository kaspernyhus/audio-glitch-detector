import signal
from threading import Event
from detectors.detect_discontinuity_stream import DetectDiscontinuitiesStream
from utils.audio_format import AudioFormat, AudioBits
from utils.rich_output import RichOutput

exit_event = Event()

DEV_ID = 15


def signal_handler(sig, frame):
    print("Exiting")
    exit_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    detect = DetectDiscontinuitiesStream(
        AudioFormat(FORMAT=AudioBits.FORMAT_32LE, CHANNELS=2, RATE=48000, CHUNK=1024),
        device_id=DEV_ID,
        save_blocks=False,
        threshold=0.1,
    )

    rich = RichOutput()
    rich.header("Audio Discontinuity Detector")

    t = detect.open(count_discontinuities=rich.increment, exit_event=exit_event)

    rich.live_output_start(exit_event=exit_event)

    rich.log("Audio processing started")
    detect.start()

    t.join()

    print("Audio processing stopped")
