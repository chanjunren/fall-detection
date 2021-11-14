import numpy as np
import pandas as pd
from  os import path
import time
import matplotlib.pyplot as plt
from math import floor
from parameters import STRIDE, TIME_STEPS
from model import MultiClassifier

BASEPATH = '../data/fall-detection'
tags = ['wrist', 'waist']
versions = ['1', '2']
labels = ['sit', 'stationary', 'walk', 'upstairs', 'downstairs']

def process():
    for label in labels:
        for version in versions:
            paths = []
            for tag in tags:
                dataset_path = path.join(BASEPATH, f'{tag}Data-{label}-{version}.csv')
                if path.isfile(dataset_path):
                    paths.append(dataset_path)
            if len(paths) != 2:
                # print(label, version, ':', 'missing waist/wrist/both', '\n')
                continue

            df = {t:None for t in tags}
            earliest = None
            latest = None
            for tag in tags:
                dataset_path = path.join(BASEPATH, f'{tag}Data-{label}-{version}.csv')
                df[tag] = pd.read_csv(dataset_path, index_col=[0])
                df[tag] =df[tag][~df[tag].index.duplicated(keep='last')]
                # print(df[tag])
                high = df[tag].index.max()
                low = df[tag].index.min()
                # print(itvl)
                if not earliest:
                    earliest = low
                    latest = high
                else:
                    earliest = max(low, earliest)
                    latest = min(latest, high)

            df['waist'] = df['waist'].loc[earliest:latest]
            df['wrist'] = df['wrist'].loc[earliest:latest]

            itvl_wa = df['waist'].index.to_numpy().copy()
            itvl_wr = df['wrist'].index.to_numpy().copy()
            itvl_wa[1:] -= itvl_wa[:-1]
            itvl_wr[1:] -= itvl_wr[:-1]
            itvl_wr[0] = 0
            itvl_wa[0] = 0
            df['waist']['interval'] = itvl_wa
            df['wrist']['interval'] = itvl_wr

            df['waist'] = df['waist'].reset_index()
            df['wrist'] = df['wrist'].reset_index()
            # print(df['waist'])
            # print(df['wrist'])
            df['waist']  = df['waist'].drop((df['waist'][df['waist'].interval == 1]).index)
            df['wrist']  = df['wrist'].drop((df['wrist'][df['wrist'].interval == 1]).index)
            to_plot = df['waist'].drop('Timestamp', axis=1).drop('interval', axis=1)
            plt.title(f'{label}_{version}')
            plt.plot(to_plot.to_numpy())
            plt.legend(to_plot.keys())
            plt.show()
            plt.waitforbuttonpress()

            to_plot = df['wrist'].drop('Timestamp', axis=1).drop('interval', axis=1)
            plt.title(f'{label}_{version}')
            plt.plot(to_plot.to_numpy())
            plt.legend(to_plot.keys())
            plt.show()
            plt.waitforbuttonpress()

            # print(df['waist'][df['waist']['interval']==1])
            merge = pd.merge_asof(df['wrist'], df['waist'], on='Timestamp', by='Timestamp', tolerance=17, direction='nearest').dropna()
            itvl = merge['Timestamp'].to_numpy().copy()
            itvl[1:] -= itvl[:-1]
            itvl[0] = 0
            # merge = merge
            merge['interval'] = itvl
            merge = merge.drop('interval_y', axis=1).drop('interval_x', axis=1).drop('interval', axis=1).drop('Timestamp', axis=1)
            # print(label, version)
            # print(merge)

            # plt.title(f'{label}_{version}')
            # plt.plot(merge.to_numpy())
            # plt.legend(merge.keys())
            # plt.show()
            # plt.waitforbuttonpress()

            # print(label, version, ":", 'wr', df['wrist'].shape, 'wa',df['waist'].shape, ' --> ', df['merge'].shape, '\n')

def to_data_set():
    x = {'train': [], 'val': [], 'test':[]}
    y = {'train': [], 'val': [], 'test':[]}
    for label in labels:
        for version in versions:
            for tag in ['waist']:
                filepath = path.join(BASEPATH, f'{tag}Data-{label}-{version}.csv')
                if not path.isfile(filepath):
                    continue

                df = pd.read_csv(filepath, index_col=[0])
                df = df[~df.index.duplicated(keep='last')]
                interval = df.index.to_numpy().copy()
                interval[1:] -= interval[:-1]
                interval[0] = 0
                df['interval'] = interval
                df = df.drop((df[df.interval < 10]).index)
                df = df.drop('interval', axis=1)
                interval = df.index.to_numpy().copy()
                interval[1:] -= interval[:-1]
                interval[0] = 0
                df['interval'] = interval
                L = df.shape[0]

                train_start = 0
                train_end = floor(L*.6)
                val_start = train_end
                val_end = floor(L*.8)
                test_start = val_end
                test_end = L

                df = df.reset_index().drop('Timestamp', axis=1).drop('interval', axis=1)
                # print(df)
                for section, section_start, section_end in [
                    ('train', train_start, train_end),
                    ('val', val_start, val_end),
                    ('test', test_start, test_end),
                ]:
                    num_samples = 0
                    for i in range(section_start, section_end-TIME_STEPS, 5):
                        window_end = i + TIME_STEPS
                        assert window_end < section_end
                        feat = df.iloc[i:window_end].to_numpy().copy()
                        feat = np.expand_dims(feat, axis=0)
                        x[section].append(feat)
                        to_idx = MultiClassifier.CLASSES_INV()
                        y[section].append(to_idx[label])
                        num_samples += 1

                    print(label, section, num_samples)

    x['train'] = np.vstack(x['train'])
    x['val'] = np.vstack(x['val'])
    x['test'] = np.vstack(x['test'])
    y['train'] = np.array(y['train'])
    y['val'] = np.array(y['val'])
    y['test'] = np.array(y['test'])

    return x, y
    # print(np.array(y))

if __name__ == "__main__":
    x,y = to_data_set()
    print(y)
