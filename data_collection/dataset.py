import pandas as pd
import numpy as np
import os
from parameters import DATA_BASE_PATH, META_CSV_HEADERS, COMB_CSV_HEADERS, MANIFEST_CSV_HEADERS
from parameters import WINDOW_SZ, TAG_PERIOD
from parameters import LABEL_NONE
from tensorflow.keras import utils
from scipy.stats import mode

def dataset_meta(dataset, period=TAG_PERIOD, window=WINDOW_SZ//2, stride=1, train=.6, val=.4, test=0, wrist=True, waist=True):
    BASE_PATH = os.path.join(DATA_BASE_PATH, 'processed', dataset)
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
            train_end = train_start + int(train*n_samples[file])
            if (train_end-train_start < window):
                print(f'{file} not included. Not enough samples for training set')
            else:
                partition['train'].append((file, train_end-train_start, train_start, train_end))


        if val > 0:
            val_start = train_end
            val_end = val_start + int(val*n_samples[file])
            if (val_end-val_start < window):
                print(f'{file} not included. Not enough samples for validation set')
            else:
                partition['val'].append((file, val_end-val_start, val_start, val_end))


        if test > 0:
            test_start = val_end
            test_end = test_start + int(test*n_samples[file])
            if (test_end-test_start < window):
                print(f'{file} not included. Not enough samples for test set')
            else:
                partition['test'].append((file, test_end-test_start, test_start, test_end))

        for part in partition:
            for (file, n, start, end) in partition[part]:
                path = os.path.join(BASE_PATH, file, csvname)
                df = pd.read_csv(path, index_col=[0]).reset_index(drop=True)

                for i in range(start, end-window, stride):
                    try:
                        label = mode(df['label'].to_numpy()[i:i+window]).mode[0]#[i:i+window]#['label']
                        if label == LABEL_NONE:
                            continue
                        if label not in meta['classes']:
                            meta['classes'][label] = 0
                            meta['train']['classes'][label] = 0
                            meta['val']['classes'][label] = 0
                            meta['test']['classes'][label] = 0
                        meta['classes'][label] += 1
                        meta[part]['classes'][label] += 1

                        meta[part]['manifest'].append((file, i, label))
                    except IndexError:
                        print(file, start, end, i , "index error")
                        break
    return meta

def df_dict_from_meta(meta):
    return {file:
        pd
        .read_csv(os.path.join(meta['root'], file, meta['csv']), index_col=[0])
        .reset_index(drop=True)
        .drop('label', axis=1) for file in meta['files']
    }




class DataGen(utils.Sequence):
    def __init__(self, batch_size=1, shuffle=True, part='train', dataset_meta=None, copy=False, seed=123, transform_x=None, transform_y=None):
        self.rng = np.random.default_rng(seed)
        self.manifest = dataset_meta[part]['manifest']
        self.n = len(self.manifest)
        self.df = df_dict_from_meta(dataset_meta)
        self.meta = dataset_meta
        self.copy = copy
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.transform_x = transform_x
        self.transform_y = transform_y

    def on_epoch_end(self):
        self.rng.shuffle(self.manifest)

    def __getitem__(self, index):
        to_get = self.manifest[index:index+self.batch_size]
        y = list(map(lambda tg: tg[2], to_get))
        x = list(map(lambda tg: self.df[tg[0]][tg[1]:tg[1]+self.meta['window']].to_numpy(), to_get))
        if self.copy:
            x = list(map(lambda z: z.copy(), x))
        if self.transform_x:
            x = self.transform_x(x)
        if self.transform_y:
            y = self.transform_y(y)

        return np.array(list(x)), np.array(list(y))

    def __len__(self):
        return self.n // self.batch_size


if __name__ == "__main__":
        # meta = dataset_meta('falldet', period=TAG_PERIOD, window=25, stride=4, train=.2, val=.8, test=0, wrist=True, waist=True)
        meta = dataset_meta('HAR', period=TAG_PERIOD, window=50, stride=2, train=.1, val=.2, test=.7, wrist=True, waist=True)

        # meta = dataset_meta('falldet', period=TAG_PERIOD, window=20, stride=10, train=.6 , val=.2, test=.2, wrist=True, waist=True)
        # meta = dataset_meta('HAR', period=TAG_PERIOD, window=80, stride=10, train=.7 , val=.2, test=.1, wrist=True, waist=True)
        print('classes', meta['classes'])
        print('classes train', meta['train']['classes'])
        print('classes val', meta['val']['classes'])
        print('classes test', meta['test']['classes'])
