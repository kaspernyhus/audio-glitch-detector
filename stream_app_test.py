import sys
import signal
import time
import threading
import numpy as np
from utils.rich_output import RichOutput
from utils.utils import get_samples_from_block
from detectors.detect_discontinuity_stream import DetectDiscontinuitiesStream, AudioFormat
from utils.key_input import KeyboardInput

exit_event = threading.Event()


if __name__ == "__main__":
    rich = RichOutput()
    rich.header("Test header")
    rich.live_output_start(exit_event)

    # detector = DetectDiscontinuitiesStream(AudioFormat())
    # detector.open(rich.increment, exit_event)

    with KeyboardInput() as keys:
        # rich.log("Press any key ('q' to exit)")
        while True:
            key = keys.getch()
            if key == "q":
                exit_event.set()
                break
            if key == "r":
                rich.reset()
                rich.log("Reset")
            if key == "s":
                if rich.is_running():
                    rich.stop()
                    rich.log("Stopped")
                else:
                    rich.start()
                    rich.log("Started")
            if key == "h":
                rich.log("Press 'q' to exit, 'r' to reset, 'p' to pause/resume the detector")

    rich.log("Exiting")
    sys.exit(0)
