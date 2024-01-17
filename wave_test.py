import numpy as np
import soundfile as sf


filename = "test_wav/sine_discont_0_stereo.wav"

file_info = sf.info(filename)
print(file_info)

num_channels = file_info.channels
num_frames = file_info.frames
sample_rate = file_info.samplerate

# current_start_frame = 0

# blocksize = 48000
# overlap = 8

# time_ms = 0

# for block in sf.blocks(filename, blocksize=blocksize, overlap=overlap, start=0):
#     print("----------------------")
#     print(f"current_start_frame: {current_start_frame}")
#     print(f"start time [ms]: {current_start_frame / (sample_rate / 1000)}")
#     num_frames_block = len(block)
#     print(f"num_frames_block: {num_frames_block}")

#     # Create an ndarray for each channel
#     if num_channels > 1:
#         block = block.T
#     else:
#         block = block.reshape(1, -1)

#     for channel in range(num_channels):
#         print(f"Channel: {channel+1}", block[channel])

#     # Update next block start time
#     current_start_frame += blocksize - overlap

data, samplerate = sf.read(filename)
if num_channels > 1:
    samples = data.T
else:
    samples = data.reshape(1, -1)

print(samples.shape)
