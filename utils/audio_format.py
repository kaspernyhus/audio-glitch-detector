import pyaudio
from dataclasses import dataclass


@dataclass
class AudioFormat:
    FORMAT: int = pyaudio.paInt16
    CHANNELS: int = 2
    RATE: int = 48000
    CHUNK: int = 1024
