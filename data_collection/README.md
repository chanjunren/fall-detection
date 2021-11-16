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
- 6 : not_falling

* falling/not_falling should not be used along with walking/stationary/etc

## PROCESSING DATA

- modify the `HAR_files`, and  `FD_files` variables in the `proces_data.py` to include the list of relevant files
- run `process_data.py` which will merge the waist/wrist data into one dataframe
- combined csv files will appear in the `HAR` and `falldet` subdirectories of the dataset directory

## DATASET METRICS

run `dataset.py` after setting the various parameters
- split ratio
- window size
- stride

the program should print the class distributions, and size of each partition (train/val/splits)

###
