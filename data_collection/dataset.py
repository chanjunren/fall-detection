import pandas as pd
import numpy as np
import os
from parameters import DATA_BASE_PATH, META_CSV_HEADERS, COMB_CSV_HEADERS, MANIFEST_CSV_HEADERS
from parameters import WINDOW_SZ, PERIOD
from tensorflow.keras import utils

def dataset_meta(period=30, window=WINDOW_SZ, stride=1, train=.6, val=.2, test=.2, wrist=True, waist=True):
    BASE_PATH = os.path.join(DATA_BASE_PATH, 'processed', 'all')

    manifest = os.path.join(BASE_PATH, 'manifest.csv')
    manifest = pd.read_csv(manifest, index_col=[0])
    manifest = manifest[manifest.period==period] #only use same period

    duration = None
    n_samples = None
    csvname = None

    if wrist and waist:
        duration = manifest.duration_comb
        n_samples = manifest.N_comb
        csvname = 'combined.csv'
    elif wrist:
        duration = manifest.duration_wrist
        n_samples = manifest.N_wrist
        csvname = 'wrist.csv'
    elif waist:
        duration = manifest.duration_waist
        n_samples = manifest.N_waist
        csvname = 'waist.csv'
    else:
        raise Exception('wrist and waist cannot both be false')

    partition = {'train':[], 'val':[], 'test':[]}

    meta = {
        'root':BASE_PATH, 'files':list(manifest.index), 'csv':csvname,
        'window':window, 'stride': stride, 'period':period,
        'split_ratio':(train,val,test),
        'classes': {},
        'train': {
            'manifest': [],
            'classes': {},
        },
        'val': {
            'manifest': [],
            'classes': {},
        },
        'test': {
            'manifest': [],
            'classes': {},
        },
    }

    for file in manifest.index:
        path = os.path.join(BASE_PATH, file, csvname)
        df = pd.read_csv(path, index_col=[0]).reset_index(drop=True)

        if train > 0:
            train_start = 0
            train_end = int(train*n_samples[file])
            if (train_end-train_start < window):
                print(f'{file} not included. Not enough samples for training set')
                continue
            partition['train'].append((file, train_end-train_start, train_start, train_end))


        if val > 0:
            val_start = train_end
            val_end = val_start + int(val*n_samples[file])
            if (val_end-val_start < window):
                print(f'{file} not included. Not enough samples for validation set')
                continue
            partition['val'].append((file, val_end-val_start, val_start, val_end))


        if test > 0:
            test_start = val_end
            test_end = int(n_samples[file])
            if (test_end-test_start < window):
                print(f'{file} not included. Not enough samples for test set')
                continue
            partition['test'].append((file, test_end-test_start, test_start, test_end))

        for part in partition:
            for (file, n, start, end) in partition[part]:
                path = os.path.join(BASE_PATH, file, csvname)
                df = pd.read_csv(path, index_col=[0]).reset_index(drop=True)

                for i in range(start, end-window, stride):
                    label = df['label'][i:i+window].mode()[0]

                    if label not in meta['classes']:
                        meta['classes'][label] = 0
                        meta['train']['classes'][label] = 0
                        meta['val']['classes'][label] = 0
                        meta['test']['classes'][label] = 0
                    meta['classes'][label] += 1
                    meta[part]['classes'][label] += 1

                    meta[part]['manifest'].append((file, i, label))
    return meta

def df_dict_from_meta(meta):
    return {file:
        pd
        .read_csv(os.path.join(meta['root'], file, meta['csv']), index_col=[0])
        .reset_index(drop=True)
        .drop('label', axis=1) for file in meta['files']
    }

class DataGen(utils.Sequence):
    def __init__(self, batch_size=1, input_shape=(10, 12), shuffle=True, part='train', copy=False, period=30, stride=2, split_ratio=(.6,.2,.2), seed=123):
        assert input_shape[1] == 12
        self.rng = np.random.default_rng(seed)
        self.meta = dataset_meta(period=period, window=input_shape[0], stride=stride, train=split_ratio[0], val=split_ratio[1], test=split_ratio[2], wrist=True, waist=True)
        self.df = df_dict_from_meta(self.meta)
        self.copy = copy
        self.manifest = self.meta[part]['manifest']
        self.n = len(self.manifest)
        self.batch_size = batch_size
        self.shuffle = shuffle

    def on_epoch_end(self):
        self.rng.shuffle(self.manifest)

    def __getitem__(self, index):
        to_get = self.manifest[index:index+self.batch_size]
        y = map(lambda tg: tg[2], to_get)
        x = map(lambda tg: self.df[tg[0]][tg[1]:tg[1]+self.meta['window']].to_numpy(), to_get)
        if self.copy:
            x = map(lambda z: z.copy(), x)
        return np.array(list(x)), np.array(list(y))

    def __len__(self):
        return self.n // self.batch_size


if __name__ == "__main__":
    meta = dataset_meta()
    # print('n_train', len(meta['train']))
    # print('n_val', len(meta['val']))
    # print('n_test', len(meta['test']))
    # print('classes', meta['classes'])
    # print('classes train', meta['train']['classes'])
    # print('classes val', meta['val']['classes'])
    # print('classes test', meta['test']['classes'])
