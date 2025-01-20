# Detect discontinuities in sine wave
Detect discontinuity in audio signals by looking at the first derivative. Only works for sine wave signals.

## Can process
- .wav file
- audio stream

## Setup using poetry
Optional:
```
poetry config virtualenvs.in-project true
```
Install dependencies
```
poetry install
```

## See options
```
poetry run detect -h
```

## How to use
### Detect discontinuities in a .wav file
```
poetry run detect -f /path/to/file
```

### Detect discontinuities in an audio stream
```
poetry run detect
```
Select audio device


## Test files
the folder `test_files/` contains files of sine tones with a known number of discontinuities
```
poetry run detect -f test_files/sine_discont_2_mono.wav
```

Outputs
```
Number of discontinuities detected:  2
0:00:01.892857
0:00:03.288367
```
