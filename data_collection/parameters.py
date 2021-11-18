import numpy as np
import logging
import os

DATA_BASE_PATH = "/Users/brian/NUS/y4s1/cs3237/fall-detection/data"
WEIGHTS_BASE_PATH = "/Users/brian/NUS/y4s1/cs3237/fall-detection/weights"

WRIST_CSV_HEADERS = [
    'timestamp(ns)', 'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz',
]

WAIST_CSV_HEADERS = [
    'timestamp(ns)', 'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
]

LABEL_CSV_HEADERS = [
    'timestamp(ns)', 'label'
]

META_CSV_HEADERS = [
    'webcam_fps', 'avg_diff', 'n_frames_data', 'n_frames_webcam', 'period', 'recording_time'
]

COMB_CSV_HEADERS = [
    'timestamp(ns)',
    'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
    'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz',
    'label',
]

MANIFEST_CSV_HEADERS = [
    'filename', 'duration', 'period', 'N_comb', 'N_waist', 'N_wrist'
]

### for labelling
LABEL_NONE    = 'NO_LABEL'
LABEL_UNKNOWN = 'unknown'
LABEL_WALKING = 'walking'
LABEL_STATION = 'stationary'
LABEL_CLIMB_U = 'climbing_up'
LABEL_CLIMB_D = 'climbing_down'
LABEL_FALLING = 'falling'
LABEL_NOT_FALLING = 'not_falling'


ID_NONE    = -1
ID_UNKNOWN = 0
ID_WALKING = 1
ID_STATION = 2
ID_CLIMB_U = 3
ID_CLIMB_D = 4
ID_FALLING = 5
ID_NOT_FALLING = 6

LABELS = [LABEL_NONE, LABEL_UNKNOWN, LABEL_WALKING, LABEL_STATION, LABEL_CLIMB_U, LABEL_CLIMB_D, LABEL_FALLING, LABEL_NOT_FALLING]
IDS    = [ID_NONE,    ID_UNKNOWN,    ID_WALKING,    ID_STATION,    ID_CLIMB_U,    ID_CLIMB_D,    ID_FALLING   , ID_NOT_FALLING]

FEATURE_LABELS = [
    'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
    'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz'
]

#
# FEATURE_LABELS = [
#     'ax', 'ay', 'az', 'gx', 'gy', 'gz'
# ]

# recording parameters
TAG_PERIOD = 30
SAMPLE_RATE = 1000/TAG_PERIOD  # TODO: update after deciding final sampling rate
WINDOW_DUR = 2.0        # TODO: update after deciding final window size
WINDOW_SZ = TIME_STEPS = int(SAMPLE_RATE * WINDOW_DUR)

# predictions client parameters
STRIDE = 20
# TIME_STEPS
# WINDOW_SZ

# parameters for encoding array  over mqtt
INPUT_TYPE_NP = np.float64
INPUT_TYPE_AR = 'd'

LOG_LEVEL = logging.INFO
