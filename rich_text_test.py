import sys
import signal
import threading
import numpy as np
from utils.rich_output import RichOutput
from utils.utils import get_samples_from_block
from detectors.detect_discontinuity_stream import DetectDiscontinuitiesStream, AudioFormat

exit_event = threading.Event()


if __name__ == "__main__":

    def signal_handler(signum, frame):
        exit_event.set()

    signal.signal(signal.SIGINT, signal_handler)

    rich = RichOutput()
    rich.header("Test header")
    rich.live_output_start(exit_event)

    detector = DetectDiscontinuitiesStream(AudioFormat())
    detector.start(rich.increment, exit_event)

    blocks = detector.get_blocks()

    for block in blocks:
        samples = get_samples_from_block(block, 2, np.int16)
        print(samples)
