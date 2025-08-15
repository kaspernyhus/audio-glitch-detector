import wave

from utils.utils import AudioFormat


def chunk2wav(chunk: bytes, filename: str, audio_format: AudioFormat):
    # Save the recorded data as a WAV file
    wf = wave.open(filename, "wb")
    wf.setnchannels(AudioFormat.CHANNELS)
    wf.setsampwidth(AudioFormat.FORMAT)
    wf.setframerate(AudioFormat.RATE)
    wf.writeframes(chunk)
    wf.close()
