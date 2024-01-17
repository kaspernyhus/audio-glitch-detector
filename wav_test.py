import numpy as np
import wave


with wave.open("test_wav/sine_discont_0_mono.wav", "rb") as wf:
    channels = wf.getnchannels()
    print("channels: ", channels)
    print("wave shape: ", wf.shape)
    print("wave")
