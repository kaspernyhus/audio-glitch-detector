from dataclasses import dataclass

import numpy as np

from .analysis import calculate_derivative, filter_nearby_glitches, find_glitch_indices


@dataclass
class DetectionResult:
    """Result of glitch detection containing timestamps and sample indices."""

    sample_indices: list[int]
    timestamps_ms: list[float]
    total_count: int


class GlitchDetector:
    """Detects audio glitches in sinusoidal signals.

    This detector works by analyzing the first derivative of audio signals
    to identify sudden discontinuities that indicate glitches in otherwise continuous signals.
    Threshold should be set so it filters out minor fluctuations that are not considered glitches.
    """

    def __init__(self, sample_rate: int, threshold: float = 0.1):
        self.sample_rate = sample_rate
        self.threshold = threshold

    def detect(self, samples: np.ndarray) -> DetectionResult:
        """Detect glitches in audio samples."""
        derivative = calculate_derivative(samples)
        discontinuities_per_channel = find_glitch_indices(derivative, self.threshold)

        # Combine all channels and remove duplicates
        all_discontinuities = []
        for channel_discontinuities in discontinuities_per_channel:
            all_discontinuities.extend(channel_discontinuities)

        filtered_discontinuities = filter_nearby_glitches(all_discontinuities)
        timestamps = [self._sample_to_milliseconds(idx) for idx in filtered_discontinuities]

        return DetectionResult(
            sample_indices=filtered_discontinuities,
            timestamps_ms=timestamps,
            total_count=len(filtered_discontinuities),
        )

    def detect_with_offset(self, samples: np.ndarray, frame_offset: int) -> DetectionResult:
        """Detect glitches in samples with absolute frame positioning."""
        result = self.detect(samples)

        # Convert relative indices to absolute
        absolute_indices = [idx + frame_offset for idx in result.sample_indices]
        absolute_timestamps = [self._sample_to_milliseconds(idx) for idx in absolute_indices]

        return DetectionResult(
            sample_indices=absolute_indices,
            timestamps_ms=absolute_timestamps,
            total_count=result.total_count,
        )

    def _sample_to_milliseconds(self, sample_index: int) -> float:
        """Convert sample index to milliseconds."""
        return (sample_index / self.sample_rate) * 1000.0
