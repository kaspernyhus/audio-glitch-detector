"""Audio Glitch Detector - Detect glitches and discontinuities in sinusoidal audio signals.

This package provides tools for detecting audio glitches in both files and real-time streams.
It works by analyzing the first derivative of audio signals to identify sudden discontinuities.

Basic usage:

File analysis:
    from audio_glitch_detector import GlitchDetector
    from audio_glitch_detector.audio import FileReader

    with FileReader("audio.wav") as reader:
        detector = GlitchDetector(reader.sample_rate, threshold=0.1)
        result = detector.detect(reader.read_all())
        print(f"Found {result.total_count} glitches")

Stream analysis:
    from audio_glitch_detector import GlitchDetector
    from audio_glitch_detector.audio import StreamReader, AudioConfig

    config = AudioConfig(sample_rate=48000, channels=2)
    with StreamReader(config) as stream:
        detector = GlitchDetector(config.sample_rate, threshold=0.1)
        # Use stream.start_monitoring() for real-time detection
"""

from .core import DetectionResult, GlitchDetector

__version__ = "0.1.0"
__all__ = ["GlitchDetector", "DetectionResult"]
