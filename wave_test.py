import numpy as np
import soundfile as sf


filename = "test_wav/sine_discont_0_stereo.wav"


for block in sf.blocks(filename, blocksize=1024, overlap=8):
    print(block.shape)
