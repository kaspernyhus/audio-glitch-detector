# Detect discontinuities in sine wave
Detect discontinuity in audio signals by looking at the first derivative. Only works for sine wave signals.

## Can process
- .wav file
- audio stream

## Setup
Make a python virtual environment and activate it
Install dependencies:
```
pip install -r requirements.txt
```

## How to use

### .wav file
```
python detect_discontinuities_file.py -h
```

### Stream
Discover audio device ID
```
python list_audio_devices.py
```

```
python detect_discontinuities_stream.py -h
```
