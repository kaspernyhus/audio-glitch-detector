import sys
import os
import pyaudio
import numpy as np
from dataclasses import dataclass

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Assuming this script is in the 'detectors' directory

if project_root not in sys.path:
    sys.path.append(project_root)

import utils.utils as utils


@dataclass
class AudioFormat:
    FORMAT: int = pyaudio.paInt16
    CHANNELS: int = 2
    RATE: int = 48000
    CHUNK: int = 1024


class DetectDiscontinuitiesStream:
    def __init__(self, format: AudioFormat, device_id=None, threshold: float = 0.1):
        self.device_id = device_id
        self.threshold = threshold
        self.p = pyaudio.PyAudio()
        self.input_stream = None
        self.AudioFormat = format

    def _process_audio_data(self, data):
        # Convert raw bytes to NumPy array
        block = np.frombuffer(data, dtype=np.int16)
        samples = utils.split_channels(block, 2)
        samples = utils.normalize_data(samples)

        abs_deriv = utils.calc_abs_derivative(samples)
        block_discont = utils.get_discontinuities(abs_deriv, threshold=0.2)

        discontinuities = []
        for channel in range(samples.shape[0]):
            discontinuities.extend(block_discont[channel])

        discont = utils.remove_duplicates(discontinuities)
        num_discont = len(discont)
        return num_discont

    def start(self):
        """Start the audio stream and process the data in realtime"""
        self.input_stream = self.p.open(
            format=self.AudioFormat.FORMAT,
            channels=self.AudioFormat.CHANNELS,
            rate=self.AudioFormat.RATE,
            input=True,
            frames_per_buffer=self.AudioFormat.CHUNK,
        )

        total_discontinuities = 0

        try:
            # for _ in range(100):
            #     input_data = input_stream.read(CHUNK)

            while True:
                input_data = self.input_stream.read(self.AudioFormat.CHUNK)
                discontinuities = self._process_audio_data(input_data)
                if discontinuities > 0:
                    total_discontinuities += discontinuities
                    print(f"Discontinuities detected: {total_discontinuities}")

        except KeyboardInterrupt:
            print("Interrupted by user")
            self.stop()

    def stop(self):
        """Stop the audio stream"""
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.p.terminate()


if __name__ == "__main__":
    print("Detecting Discontinuities in sine waves realtime")
    AudioFormat = AudioFormat(FORMAT=pyaudio.paInt16, CHANNELS=2, RATE=48000, CHUNK=1024)
    detector = DetectDiscontinuitiesStream(AudioFormat)
    detector.start()
