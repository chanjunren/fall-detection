# from tensorflow import __version__ as __tensorflow_version__
# from numpy import __version__ as __numpy_version__
# print("TENSORFLOW_VERSION", __tensorflow_version__)
# print("NUMPY_VERSION", __numpy_version__)

import numpy as np
import matplotlib.pyplot as plt
from h5py import is_hdf5
from os.path import exists as path_exists
from tensorflow.keras import layers
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.callbacks import EarlyStopping
from abc import ABC, abstractmethod
from sklearn.metrics import confusion_matrix, plot_confusion_matrix
from sklearn.preprocessing import LabelBinarizer
from parameters import INPUT_SHAPE

class Classifier(ABC):
    @classmethod
    @abstractmethod
    def N_CLASSES(cls):
        pass

    @classmethod
    @abstractmethod
    def CLASSES(cls):
        pass

    @classmethod
    @abstractmethod
    def get_and_compile_fresh_model(cls):
        pass

    @classmethod
    @abstractmethod
    def decode_prediction(cls, y_pred, threshold=.5, tostring=True):
        pass

    @classmethod
    @abstractmethod
    def encode_target(cls, y_target):
        pass

    def __init__(self, src_path=None):
        self.src_path = src_path
        if src_path and is_hdf5(src_path):
            print(f'Loading model from {src_path}.')
            self.model = load_model(path)
        else:
            print(f'Initializing untrained [{self.__class__.__name__}]model.')
            self.model = self.__class__.get_and_compile_fresh_model()

    def predict(self, x):
        if x.ndim == 2:
           x = np.expand_dims(x, 0)
        assert x.ndim == 3
        return self.model.predict(x)

    @staticmethod
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

    def save(self, dst_path, overwrite, verbose=1):
        if not dst_path:
            dst_path = self.src_path

        if verbose>0:
            print(
                '',
                '----------------',
                f"Saving Model to '{dst_path}'",
                '----------------',
                sep='\n'
                )

        if overwrite=='error' and path_exists(dst_path):
            raise FileExistsError(dst_path)
        elif overwrite=='prompt':
            self.model.save(dst_path, overwrite=False, save_format='h5')
        elif overwrite=='overwrite':
            self.model.save(dst_path, overwrite=True, save_format='h5')
        else:
            raise ValueError("overwrite must be 'overwrite', 'prompt', or 'error'!")

    def train(
        self, x, y, n_epochs, batch_sz, early_stop=False,
        display_graph=False,
        save=True, dst_path=None, overwrite='prompt',
        verbose=1
        ):

        for split in y:
            y[split] = self.encode_target(y[split])

        fit_callbacks = []
        if early_stop:
            fit_callbacks.append(EarlyStopping(monitor='val_loss', patience=2, mode='min'))

        if verbose > 0:
            print(
                '',
                '----------------',
                'Training Model',
                '----------------',
                sep='\n'
                )
        hist = self.model.fit(
                    x['train'],
                    y['train'],
                    epochs=n_epochs,
                    validation_data=(x['val'], y['val']),
                    batch_size=batch_sz,
                    verbose=verbose,
                    callbacks=fit_callbacks,
                    )

        loss = None
        accuracy = None
        if 'test' in x and 'test' in y:
            if verbose > 0:
                print(
                    '',
                    '----------------',
                    'Evaluating Model',
                    '----------------',
                    sep='\n'
                    )
            loss, accuracy = self.model.evaluate(x['test'], y['test'], batch_size=batch_sz, verbose=verbose)

        if display_graph:
            Classifier.plot_training_progress(hist, verbose=verbose)

        if save:
            self.save(dst_path, overwrite, verbose=verbose)

        return hist, loss, accuracy

class BinaryClassifier(Classifier):
    @classmethod
    def CLASSES(cls):
        return {0: 'not_fall', 1: 'fall'}

    @classmethod
    def N_CLASSES(cls):
        return 2

    @classmethod
    def get_and_compile_fresh_model(cls):
        model = Sequential([
            layers.LSTM(128, input_shape=INPUT_SHAPE),
            layers.Dropout(.5),
            layers.Dense(units=64, activation='relu'),
            layers.Dense(units=1, activation='sigmoid'),
        ])
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    @classmethod
    def decode_prediction(cls, y_pred, threshold=.5, tostring=True):
        if tostring:
            return np.where(y_pred > threshold, cls.CLASSES()[1], cls.CLASSES()[0])
        else:
            return np.where(y_pred > threshold, 1 , 0)

    @classmethod
    def encode_target(_, y_target):
        return y_target

class MultiClassifier(Classifier):
    @classmethod
    def CLASSES(cls):
        # example classes
        return {0: 'walking', 1: 'falling', 2: 'stationary', -1:'unknown'}

    @classmethod
    def N_CLASSES(cls):
        return 3

    @classmethod
    def get_and_compile_fresh_model(cls):
        model = Sequential([
            layers.LSTM(128, input_shape=INPUT_SHAPE),
            layers.Dropout(.5),
            layers.Dense(units=64, activation='relu'),
            layers.Dense(units=cls.N_CLASSES(), activation='softmax'),
        ])
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    @classmethod
    def decode_prediction(cls, y_pred, threshold=.5, tostring=True):
        which_class = y_pred.argmax(1)
        idx = np.unravel_index(which_class, y_pred.shape)
        decision = np.where(y_pred[idx] > threshold, which_class, -1)
        if tostring:
            decision = list(map(lambda y: cls.CLASSES()[y], decision))
        return decision

    @classmethod
    def encode_target(cls, y_target):
        n_classes = cls.N_CLASSES()
        assert n_classes > 2

        enc = LabelBinarizer()
        enc.fit(range(n_classes))
        onehot = enc.transform(y_target)
        return onehot

if __name__ == "__main__":
    class Fake:
        '''
        Generate fake data in required shape.
        '''
        def x_fake(n):
            return np.random.uniform(-3, 3, (n, INPUT_SHAPE[0], INPUT_SHAPE[1]))

        def y_fake(n, n_classes=1):
            if n_classes in [1,2]:
                return np.random.randint(0,2, (n,1))
            assert n_classes > 2
            return np.random.randint(0, n_classes, (n,1))

        def __init__(self, n):
            self.n = n

        def get_x(self):
            return {
                'train': Fake.x_fake(10*self.n),
                'test': Fake.x_fake(self.n),
                'val': Fake.x_fake(self.n),
            }

        def get_y(self, n):
            return {
                'train': Fake.y_fake(10*self.n, n),
                'test': Fake.y_fake(self.n, n),
                'val': Fake.y_fake(self.n, n),
            }

    ##  model with more depth (stacking LSTM cells)

    # class MC2(MultiClassifier):
    #     @classmethod
    #     def CLASSES(cls):
    #         return {0: 'walking', 1: 'jumping', 2:'croaking', 3:'flying', -1:'unknown'}
    #
    #     @classmethod
    #     def N_CLASSES(cls):
    #         return 4
    #
    #     @classmethod
    #     def get_and_compile_fresh_model(cls):
    #         model = Sequential([
    #             layers.LSTM(128, return_sequences=True, input_shape=INPUT_SHAPE),
    #             layers.LSTM(64),
    #             layers.Dropout(.5),
    #             layers.Dense(units=32, activation='relu'),
    #             layers.Dense(units=cls.N_CLASSES(), activation='softmax'),
    #         ])
    #         model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    #         return model

    mo = MultiClassifier()
    fake_data_gen = Fake(20)
    n = mo.N_CLASSES()
    x = fake_data_gen.get_x()
    y = fake_data_gen.get_y(n)

    mo.train(x, y, 10, 5, display_graph=True, dst_path='temp2', overwrite='overwrite', verbose=0)
