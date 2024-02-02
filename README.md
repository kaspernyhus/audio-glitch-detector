# Detect discontinuities in sine wave
Detect discontinuity by looking at the first derivative. Only works for sine wave signals.

## Setup
OPTIONAL: make a python virtual environment and activate it
Install dependencies:
```
pip install -r requirements.txt
```

## How to use
```
python detect_discontinuity.py <file.wav>
```


### Use class as content manager
```
 with DetectDiscontinuities(filename, threshold) as dd:
        dd.process_blocks()
        dd.show_results()
```

