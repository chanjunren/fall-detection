# from tensorflow import __version__ as __tensorflow_version__
# from numpy import __version__ as __numpy_version__
# print("TENSORFLOW_VERSION", __tensorflow_version__)
# print("NUMPY_VERSION", __numpy_version__)
# exit()
import matplotlib.pyplot as plt
import numpy as np
import os
from abc import ABC, abstractmethod
from os.path import exists as path_exists
from tensorflow.keras import layers
from tensorflow.keras.models import load_model as k_load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import LabelBinarizer
from parameters import TIME_STEPS, TAG_PERIOD, WINDOW_SZ, WEIGHTS_BASE_PATH

# TIME_STEPS == 66

def multi_f_c(f, c):
    assert c > 3
    return [
        layers.LSTM(128, input_shape=(TIME_STEPS, f)),
        layers.Dropout(.5),
        layers.Dense(units=64, activation='relu'),
        layers.Dense(units=c, activation='softmax'),
    ]

def binary_f_c(f, c):
    assert c in [1,2]
    return [
        layers.LSTM(100, return_sequences=True, input_shape=(40, f)),
        layers.Dropout(.3),
        layers.LSTM(100, ),
        layers.Dropout(.3),
        layers.Dense(units=50, activation='relu'),
        layers.Dense(units=1, activation='sigmoid'),
    ]

def compile(model, binary):
    if binary:
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    else:
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def get_model(name, features, classes, is_binary):
    if name == 'model_multi':
        f = len(features)
        c = len(classes)
        return Sequential(multi_f_c(f,c), name=f'{name}_{f}_{c}')

    elif name == 'model_binary':
        f = len(features)
        c = len(classes)
        return Sequential(binary_f_c(f,c), name=f'{name}_{f}_{1}')

    else:
        raise Exception('name must be either model_binary or model_multi')

def load_model(model, version):
    src_path = os.path.join(WEIGHTS_BASE_PATH, f'{model.name}_v{version}.h5')
    if path_exists(src_path):
        print('load from', src_path)
        return k_load_model(src_path)
    else:
        print('no saved model @', src_path)
        return None

def save_model(model, version, overwrite=True):
    dst_path = os.path.join(WEIGHTS_BASE_PATH, f'{model.name}_v{version}.h5')
    print('save to', dst_path)
    model.save(dst_path, overwrite=overwrite)

def plot_training_progress(hist, verbose=1):
    if verbose>0:
        print(
            '',
            '----------------------------',
            'Displaying Training Progress',
            '* Press ANY key to continue.',
            '----------------------------',
            sep='\n'
            )
    fig = plt.figure()
    fig.suptitle('Progress')
    f1 = fig.add_subplot(2, 1, 1, xlabel='epoch', ylabel='loss')
    f2 = fig.add_subplot(2, 1, 2, xlabel='epoch', ylabel='accuracy')
    f1.plot(np.array(hist.history['loss']), 'r-', label='train')
    f1.plot(np.array(hist.history['val_loss']), 'r--', label='val')
    f2.plot(np.array(hist.history['accuracy']), 'g-', label='train')
    f2.plot(np.array(hist.history['val_accuracy']), 'g--', label='val')
    f1.legend(loc='upper left')
    f2.legend(loc='upper left')
    fig.show()
    plt.waitforbuttonpress()


def train(model, train_gen, val_gen, test_gen, n_epochs, batch_sz, early_stop, dst_version, verbose=True):
    fit_callbacks = []
    if early_stop:
        fit_callbacks.append(EarlyStopping(monitor='val_loss', patience=2, mode='min'))

    print('\nTRAINING MODEL....\n')
    hist = model.fit(
                train_gen,
                epochs=n_epochs,
                validation_data=val_gen,
                batch_size=batch_sz,
                verbose=1 if verbose else 2,
                callbacks=fit_callbacks,
                )

    loss, accuracy = None, None

    if test_gen:
        print('\nEVALUATING MODEL....\n')
        loss, accuracy = model.evaluate(test_gen, batch_size=batch_sz, verbose=verbose)

    if verbose:
        plot_training_progress(hist)

    if dst_version:
        save_model(model, dst_version)

    return hist, loss, accuracy


def encode_label_to_target(y_label, classes, binary):
    to_idx = {cls: i for i,cls in enumerate(classes)}
    target = to_idx[y_label]

    if not binary:
        enc = LabelBinarizer()
        enc.fit(range(len(classes)))
        target = enc.transform(target)

    return target

def decode_prediction_binary(prediction, threshold=.5, classes=None):
    positive = classes[1] if classes else 1
    negative = classes[0] if classes else 0
    return np.where(prediction > threshold, positive , negative).tolist(), prediction.tolist()

def decode_prediction_multi(prediction, threshold=0, classes=None):
    # sort by confidence in descending order
    pred_sort = np.sort(prediction, 1)[:,::-1]
    which_class = prediction.argsort(1)[:,::-1]
    decision = None
    if classes:
        classes = np.array(classes)
        decision = np.array(classes)[which_class]
        low_conf = np.array(list(map(lambda x: f'{x} (low confidence)', classes)))
        decision = np.where(pred_sort > threshold, classes, low_conf).tolist()
    else:
        decision = which_class.tolist()

    return decision, pred_sort.tolist()

def get_binary_model(version, six=False):
    classes=['not_falling', 'falling']

    features=[
        'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
        'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz'
    ]
    if six:
        features=[
            'ax', 'ay', 'az', 'gx', 'gy', 'gz',
        ]

    model2 = get_model('model_binary', features, classes, True)
    loaded = load_model(model2, version)

    def transform_y(ys):
        return list(map(lambda y: encode_label_to_target(y, classes, True), ys))

    if loaded:
        model2 = loaded
    else:
        compile(model2, True)

    return model2, features, classes, transform_y

def get_multi_model(version, six=False):
    classes=['walking','stationary','climbing_up','climbing_down']
    features=[
        'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
        'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz'
    ]

    if six:
        features=[
            'ax', 'ay', 'az', 'gx', 'gy', 'gz',
        ]

    model2 = get_model('model_multi', features, classes, False)
    loaded = load_model(model2, version)

    def transform_y(ys):
        return list(map(lambda y: encode_label_to_target(y, classes, False), ys))

    if loaded:
        model2 = loaded
    else:
        compile(model2, False)

    return model2, features, classes, transform_y


if __name__ == "__main__":
    import sys
    sys.path.append('../data_collection')
    import dataset

    # 10
    # 11
    # 12
    # 13
    # 14
    # 15 100-100-50
    # 16  split sets
    #
    version = 16
    model, features, classes, transform_y = get_binary_model(version)
    # model, features, classes, transform_y = get_multi_model(version)

    meta = dataset.dataset_meta('falldet', period=TAG_PERIOD, window=40, stride=5, train=.2, val=.1, test=.7, wrist=True, waist=True)
    val_gen  = dataset.DataGen(dataset_meta=meta, part='train', transform_y=transform_y)
    test_gen  = dataset.DataGen(dataset_meta=meta, part='val', transform_y=transform_y)
    train_gen = dataset.DataGen(dataset_meta=meta, part='test', transform_y=transform_y)
    train(model, train_gen, val_gen, test_gen, 10, 10, False, version)
