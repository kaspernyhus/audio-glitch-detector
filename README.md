# Detect discontinuities in sine wave
Detect discontinuity in audio signals by looking at the first derivative. Only works for sine wave signals.

## Modes
- file
- stream

File mode can analyze .wav files
Stream will open a portAudio device that can be used for realtime analysis

## Setup
OPTIONAL: make a python virtual environment and activate it
Install dependencies:
```
pip install -r requirements.txt
```

## How to use
```
python detect_discontinuity.py -h
```
