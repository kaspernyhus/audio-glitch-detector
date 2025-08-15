import time
import pyaudio
from threading import Event, Thread
from typing import Callable
from audio_glitch_detector.utils.audio_format import AudioFormat
from audio_glitch_detector.utils import utils, audio_meter
from audio_glitch_detector.utils.dsp import calc_abs_derivative, normalize_data, split_channels, get_samples_from_block, convert_to_float


class DiscontinuityDetectorStream:
    def __init__(self, format: AudioFormat, device_id=None, detection_threshold: float = 0.1, save_blocks: bool = False, signal_threshold: float = -40.0) -> None:
        self.device_id = device_id
        self.detection_threshold = detection_threshold
        self.p = pyaudio.PyAudio()
        self.input_stream = None
        self.AudioFormat: AudioFormat = format
        self.save_blocks = save_blocks
        self.saved_blocks = []
        self.running = False
        self.meter = audio_meter.Meter()
        self.signal_threshold = signal_threshold

    def _process_audio_data(self, data):
        # Convert raw bytes to NumPy array
        samples = get_samples_from_block(
            block=data, channels=self.AudioFormat.CHANNELS, bit_depth=self.AudioFormat.FORMAT
        )
        samples = split_channels(samples, self.AudioFormat.CHANNELS)
        samples = convert_to_float(samples)
        
        # If signal level is below threshold, ignore
        self.meter.update(samples)
        if all(peak < self.signal_threshold for peak in self.meter.get_peak()):
            return 0
        
        samples = normalize_data(samples)

        abs_deriv = calc_abs_derivative(samples)
        block_discont = utils.count_discontinuities(abs_deriv, threshold=0.2)

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
                    self.close()
                    break

                if not self.running:
                    time.sleep(0.1)
                    continue

                try:
                    input_data = self.input_stream.read(self.AudioFormat.CHUNK)
                    discontinuities = self._process_audio_data(input_data)
                    if discontinuities > 0:
                        count_discontinuities(discontinuities)
                        if self.save_blocks:
                            self.saved_blocks.append(input_data)
                except OSError as e:
                    print(f"Error reading audio data: {e}")

        except KeyboardInterrupt:
            self.close()

    def _open_stream(self):
        """Open the audio stream"""
        if self.AudioFormat.FORMAT == 16:
            format = pyaudio.paInt16
        if self.AudioFormat.FORMAT == 32:
            format = pyaudio.paInt32

        self.input_stream = self.p.open(
            format=format,
            channels=self.AudioFormat.CHANNELS,
            rate=self.AudioFormat.RATE,
            input_device_index=self.device_id,
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

    def get_saved_blocks(self):
        return self.saved_blocks

    def get_meter_data(self):
        return self.meter.get_peak()
