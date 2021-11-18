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
from tensorflow.keras import regularizers
from tensorflow.keras.models import load_model as k_load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import label_binarize
from parameters import TIME_STEPS, TAG_PERIOD, WINDOW_SZ, WEIGHTS_BASE_PATH
from scipy import signal
fs = 1000/TAG_PERIOD
# TIME_STEPS == 66

def multi_f_c(f, c):
    assert c > 3
    return [
        layers.LSTM(60, return_sequences=True, input_shape=(50, f)),
        layers.Dropout(.5),
        layers.LSTM(60, activity_regularizer=regularizers.L1(0.01), return_sequences=True),
        layers.Dropout(.5),
        layers.LSTM(30, activity_regularizer=regularizers.L2(0.01)),
        layers.Dropout(.5),
        layers.Dense(units=30, activity_regularizer=regularizers.L2(0.01), activation='relu'),
        layers.Dense(units=c, activation='softmax'),
    ]

def binary_f_c(f, c):
    assert c in [1,2]
    return [
        layers.LSTM(20, input_shape=(50, f), return_sequences=True),
        layers.Dropout(.5),
        layers.LSTM(20, activity_regularizer=regularizers.L1(0.01)),
        layers.Dropout(.5),
        layers.Dense(units=5, activation='relu', activity_regularizer=regularizers.L2(0.01)),
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

    if dst_version is not None:
        save_model(model, dst_version)

    return hist, loss, accuracy


def encode_label_to_target(y_label, classes, binary):
    if binary:
        to_idx = {cls: i for i,cls in enumerate(classes)}
        target = to_idx[y_label]
    else:
        target = label_binarize([y_label], classes=classes)[0]
    return target

def decode_prediction_binary(prediction, threshold=.5, classes=None):
    positive = classes[1] if classes else 1
    negative = classes[0] if classes else 0
    return np.where(prediction > threshold, positive , negative).tolist(), prediction.tolist()

def decode_prediction_multi(prediction, threshold=0, classes=None):
    # sort by confidence in descending order
    pred_sort = np.sort(prediction, 1)[:,::-1]
    print('1', pred_sort)

    which_class = prediction.argsort(1)[:,::-1]
    print('1', which_class)
    decision = None
    if classes:
        decision = np.array(classes)[which_class]
        low_conf = np.array(list(map(lambda x: f'{x} (low confidence)', classes)))[which_class]
        decision = np.where(pred_sort > threshold, decision, low_conf).tolist()
    else:
        decision = which_class.tolist()

    return decision, pred_sort.tolist()

def get_binary_model(version):
    classes=['not_falling', 'falling']

    features=[
        'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
        'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz'
    ]*2

    features = ['placeholder']*28

    model2 = get_model('model_binary', features, classes, True)
    loaded = load_model(model2, version)
    print('aaaa')
    def transform_y(ys):
        return list(map(lambda y: encode_label_to_target(y, classes, True), ys))

    def transform_x(x):
        sig = np.array(x)
        denos = signal.butter(3, 15/(fs/2), 'low', output='sos')
        med = signal.medfilt(sig, kernel_size=(1,3,1))
        den = signal.sosfilt(denos, med, axis=1)
        gyr = np.dstack([
            den[:,:,3:6],
            den[:,:,9:12]
        ])/360
        accwa = den[:,:,0:3]
        accwr = den[:,:,6:9]
        losos = signal.butter(2, 2/(fs/2), 'low', output='sos')
        lowa = signal.sosfilt(losos, accwa,axis=1)
        lowr = signal.sosfilt(losos, accwr,axis=1)
        remwa = accwa - lowa
        remwr = accwr - lowr
        magrwa = np.linalg.norm(remwa,axis=2)
        magrwr = np.linalg.norm(remwr,axis=2)
        maglwa = np.linalg.norm(lowa,axis=2)
        maglwr = np.linalg.norm(lowr,axis=2)
        ret = np.dstack([
            accwa,
            magrwa,
            remwa,
            maglwa,
            lowa,
            accwr,
            magrwr,
            remwr,
            maglwr,
            lowr,
            gyr
        ])
        return ret

    if loaded:
        model2 = loaded
    else:
        compile(model2, True)

    return model2, features, classes, transform_y, transform_x

def get_multi_model(version):
    classes=['walking','stationary','climbing_up','climbing_down']
    features=[
        'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
        'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz'
    ]*2
    features = ['placeholder']*28

    model2 = get_model('model_multi', features, classes, False)
    loaded = load_model(model2, version)
    print('bbbb')

    def transform_y(ys):
        return list(map(lambda y: encode_label_to_target(y, classes, False), ys))

    if loaded:
        model2 = loaded
    else:
        compile(model2, False)

    def transform_x(x):
        sig = np.array(x)
        denos = signal.butter(3, 15/(fs/2), 'low', output='sos')
        med = signal.medfilt(sig, kernel_size=(1,3,1))
        den = signal.sosfilt(denos, med, axis=1)
        gyr = np.dstack([
            den[:,:,3:6],
            den[:,:,9:12]
        ])/360
        accwa = den[:,:,0:3]
        accwr = den[:,:,6:9]
        losos = signal.butter(2, 2/(fs/2), 'low', output='sos')
        lowa = signal.sosfilt(losos, accwa,axis=1)
        lowr = signal.sosfilt(losos, accwr,axis=1)
        remwa = accwa - lowa
        remwr = accwr - lowr
        magrwa = np.linalg.norm(remwa,axis=2)
        magrwr = np.linalg.norm(remwr,axis=2)
        maglwa = np.linalg.norm(lowa,axis=2)
        maglwr = np.linalg.norm(lowr,axis=2)
        ret = np.dstack([
            accwa,
            magrwa,
            remwa,
            maglwa,
            lowa,
            accwr,
            magrwr,
            remwr,
            maglwr,
            lowr,
            gyr
        ])
        return ret


    return model2, features, classes, transform_y, transform_x

def not_fall_transformer(ys):
    return [0 for _ in ys]

if __name__ == "__main__":
    import sys
    sys.path.append('../data_collection')
    import dataset

    # fall
    # 0 - trained on fall, 60/20/20 split, 20/2 w/s
    # 1 - trained on har as non-fall, 15/15/15 split 20/100 ws
    # 2 - trained on har as non-fall, 15/15/15 split 20/150 ws
    #
    # 4 - 7/3 split 2 lstm stack, l1,l2 regularizers
    # 5 - trained on har for not fall
    # 10 epoch, w early stopping, batchsz 100
    # 6 - 95 acc, 12->28 features, 40,40 lstm
    # 7 = + har
    # 10/11
    # 12/13  $50 window, 2/8 val/train



    version = 19
    model, features, classes, transform_y, transform_x = get_multi_model(version)
    meta = dataset.dataset_meta('HAR', period=TAG_PERIOD, window=50, stride=4, train=.1, val=.2, test=.7, wrist=True, waist=True)
    har_gen = dataset.DataGen(dataset_meta=meta, part='test', batch_size=16, transform_y=transform_y, transform_x=transform_x)
    val_gen = dataset.DataGen(dataset_meta=meta, part='val', batch_size=4, transform_y=transform_y, transform_x=transform_x)
    test_gen = dataset.DataGen(dataset_meta=meta, part='train', batch_size=1, transform_y=transform_y, transform_x=transform_x)
    train(model, har_gen, val_gen, test_gen, 10, 20, True, 19)

    # version=12
    # batch_sz = 2
    # model, features, classes, transform_y, transform_x = get_binary_model(version)
    # meta = dataset.dataset_meta('falldet', period=TAG_PERIOD, window=50, stride=2, train=.2, val=.8, test=0, wrist=True, waist=True)
    # train_gen  = dataset.DataGen(dataset_meta=meta, part='val', batch_size=batch_sz, transform_y=transform_y, transform_x=transform_x)
    # val_gen  = dataset.DataGen(dataset_meta=meta, part='train', batch_size=batch_sz, transform_y=transform_y, transform_x=transform_x)
    # # test_gen = dataset.DataGen(dataset_meta=meta, part='test', transform_y=transform_y, transform_x=transform_x)
    # test_gen = None
    # train(model, train_gen, val_gen, test_gen, 8, batch_sz, True, 12)
    #
    # meta = dataset.dataset_meta('HAR', period=TAG_PERIOD, window=50, stride=2, train=.4, val=.3, test=.3, wrist=True, waist=True)
    # train_gen = dataset.DataGen(dataset_meta=meta, part='train', batch_size=30, transform_x=transform_x, transform_y=not_fall_transformer)
    # val_gen = dataset.DataGen(dataset_meta=meta, part='val', batch_size=10, transform_x=transform_x, transform_y=not_fall_transformer)
    # test_gen = dataset.DataGen(dataset_meta=meta, part='test', batch_size=10, transform_x=transform_x, transform_y=not_fall_transformer)
    # train(model, train_gen, val_gen, None, 2, 1, True, 13)
