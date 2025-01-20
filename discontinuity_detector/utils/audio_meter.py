import numpy as np
import math


class Meter:
    """Simple VU meter"""

    def __init__(self):
        self.peak_raw = [0.0, 0.0]
        self.peak_db = [0.0, 0.0]
        self.bias = 1.0

    def update(self, samples: np.ndarray):
        num_channels = samples.shape[0]

        for channel in range(num_channels):
            peak = np.max(np.abs(samples[channel]))

            if peak > self.peak_raw[channel]:
                self.peak_raw[channel] = peak

    def get_peak(self):
        for i in range(2):
            if self.peak_raw[i] > 0.0:
                self.peak_db[i] = 20.0 * math.log10(self.peak_raw[i])
            self.peak_raw[i] = 0.0
        return self.peak_db
