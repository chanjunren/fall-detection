## COLLECTING DATA

run `python3 record_save_label.py`

Process will tag for both sensor tags to connect,

Then after a short delay, the `START` message will appear, and the processes will run.

Afterwards, a cv2 window will open showing the various frames captured during the recording process

- left arrow  : decrement frames by step size
- right arrow : increment frames by step size
- up arrow : increment step size
- down arrow : decrement step size
- q/esc : quit
- NUMBER keys to label
- 1 : walking
- 2 : stationary
- 3 : climbing_up
- 4 : climbing_down
- 5 : falling

## PROCESSING DATA

run `process_data.py` which will merge the waist/wrist data into one dataframe

## DATASET METRICS

run `dataset.py` after setting the various parameters
- split ratio
- window size
- stride

the program should print the class distributions, and size of each partition (train/val/splits)


###
