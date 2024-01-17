# Detect discontinuities in sine wave
Detect discontinuity by looking at the first derivative. Only works for sine wave signals.

### How to use
```
python detect_discontinuity.py <file.wav>
```


### Use class as content manager
```
 with DetectDiscontinuities(filename, threshold) as dd:
        dd.process_blocks()
        dd.show_results()
```

