import pyaudio
from dataclasses import dataclass


@dataclass
class AudioBits:
    FORMAT_16LE: int = 16
    FORMAT_32LE: int = 32


@dataclass
class AudioFormat:
    FORMAT: AudioBits = AudioBits.FORMAT_16LE
    CHANNELS: int = 2
    RATE: int = 48000
    CHUNK: int = 1024
