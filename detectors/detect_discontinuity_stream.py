import sys
import os
import signal
import time
import pyaudio
import numpy as np
from threading import Event, Thread
from typing import Callable
from utils.audio_format import AudioFormat

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

import utils.utils as utils


class DetectDiscontinuitiesStream:
    def __init__(self, format: AudioFormat, device_id=None, threshold: float = 0.1, save_blocks: bool = False) -> None:
        self.device_id = device_id
        self.threshold = threshold
        self.p = pyaudio.PyAudio()
        self.input_stream = None
        self.AudioFormat = format
        self.save_blocks = save_blocks
        self.saved_blocks = []
        self.running = False

    def _process_audio_data(self, data):
        # Convert raw bytes to NumPy array
        samples = utils.get_samples_from_block(block=data, channels=self.AudioFormat.CHANNELS, bit_depth=np.int16)

        abs_deriv = utils.calc_abs_derivative(samples)
        block_discont = utils.get_discontinuities(abs_deriv, threshold=0.2)

        discontinuities = []
        for channel in range(samples.shape[0]):
            discontinuities.extend(block_discont[channel])

        discont = utils.remove_duplicates(discontinuities)
        num_discont = len(discont)
        return num_discont

    def _run(self, exit_event: Event, count_discontinuities: Callable[[int], None]) -> None:
        try:
            while True:
                if exit_event.is_set():
                    print("Closing audio processing")
                    self.close()
                    break

                if not self.running:
                    time.sleep(0.1)
                    continue

                input_data = self.input_stream.read(self.AudioFormat.CHUNK)
                discontinuities = self._process_audio_data(input_data)
                if discontinuities > 0:
                    count_discontinuities(discontinuities)
                    if self.save_blocks:
                        self.saved_blocks.append(input_data)

        except KeyboardInterrupt:
            print("Interrupted by user")
            self.stop()

    def _open_stream(self):
        self.input_stream = self.p.open(
            format=self.AudioFormat.FORMAT,
            channels=self.AudioFormat.CHANNELS,
            rate=self.AudioFormat.RATE,
            input=True,
            frames_per_buffer=self.AudioFormat.CHUNK,
        )

    def open(self, count_discontinuities: Callable[[int], None], exit_event: Event):
        """Start the audio stream and process the data in realtime"""
        self._open_stream()
        audio_thread = Thread(target=self._run, args=(exit_event, count_discontinuities))
        audio_thread.start()
        return audio_thread

    def start(self):
        """Start the audio stream"""
        self.running = True
        print("Audio processing started")

    def stop(self):
        """Pause the audio stream"""
        self.running = False

    def close(self):
        """Stop the audio stream"""
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.p.terminate()

    def reset(self):
        """Reset the saved blocks"""
        self.saved_blocks = []
        print("Saved blocks reset")

    def get_saved_blocks(self):
        return self.saved_blocks


if __name__ == "__main__":
    exit_event = Event()

    def signal_handler(signum, frame):
        exit_event.set()

    signal.signal(signal.SIGINT, signal_handler)

    print("Detecting Discontinuities in sine waves realtime")
    AudioFormat = AudioFormat(FORMAT=pyaudio.paInt16, CHANNELS=2, RATE=48000, CHUNK=1024)
    detector = DetectDiscontinuitiesStream(AudioFormat)

    def logger(int):
        print(int)

    audio_thread = detector.open(logger, exit_event)
    detector.start()
    print("Audio processing started")

    print("Press Ctrl+C to stop")
    audio_thread.join()
    print("Audio processing stopped")
