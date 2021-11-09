SAMPLE_RATE = 90 # TODO: update after deciding final sampling rate
WINDOW_SECONDS = 1 # TODO: update after deciding final window size

TIME_STEPS = int(SAMPLE_RATE * WINDOW_SECONDS)

# FEATURE_LABELS = ['a_x', 'a_y', 'a_z', 'g_x', 'g_y', 'g_z']
# N_FEATURES = 6

FEATURE_LABELS = [
    'wrist_a_x', 'wrist_a_y', 'wrist_a_z', 'wrist_g_x', 'wrist_g_y', 'wrist_g_z',
    'hip_a_x', 'hip_a_y', 'hip_a_z', 'hip_g_x', 'hip_g_y', 'hip_g_z'
]

N_FEATURES = len(FEATURE_LABELS)
INPUT_SHAPE = (TIME_STEPS, N_FEATURES)
