
Dependencies
------------
* bleak
* pyaudio
* wave ?

* Fusion - to be compile using local copy


## Data collection:
Run using ```python data-stream.py```
In sensortag firmware, load the ```sensortag_cc2650app example```
Edit the following lines to the values below in the ```sensortag_mov.c``` file
``` 
    #define SENSOR_DEFAULT_PERIOD     25
    #define GYR_SHAKE_THR             0
    #define WOM_THR                   0
```

Currently set to record about 60s worth of data in 1 run