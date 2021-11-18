import pandas as pd
import os

from parameters import DATA_BASE_PATH, META_CSV_HEADERS, COMB_CSV_HEADERS, MANIFEST_CSV_HEADERS

def combine(filename, dataset, verbose=False):
    FOLDER_PATH_IN = os.path.join(DATA_BASE_PATH, 'unprocessed', filename)
    FOLDER_PATH_OUT = os.path.join(DATA_BASE_PATH, 'processed', dataset)

    if not os.path.exists(os.path.join(FOLDER_PATH_OUT, filename)):
        os.makedirs(os.path.join(FOLDER_PATH_OUT, filename))

    if not os.path.exists(FOLDER_PATH_IN):
        raise FileExistsError('Please specify valid input directory name')

    WAIST_IN_PATH = os.path.join(FOLDER_PATH_IN, 'waist.csv')
    WRIST_IN_PATH = os.path.join(FOLDER_PATH_IN, 'wrist.csv')
    LABEL_IN_PATH = os.path.join(FOLDER_PATH_IN, 'label.csv')
    META_IN_PATH  = os.path.join(FOLDER_PATH_IN, 'meta.csv')

    COMB_OUT_PATH = os.path.join(FOLDER_PATH_OUT, filename, 'combined.csv')
    WAIST_OUT_PATH = os.path.join(FOLDER_PATH_OUT, filename, 'waist.csv')
    WRIST_OUT_PATH = os.path.join(FOLDER_PATH_OUT, filename, 'wrist.csv')

    MANIFEST_PATH = os.path.join(FOLDER_PATH_OUT, 'manifest.csv')

    df_wa = df_wa_og = pd.read_csv(WAIST_IN_PATH, index_col=[0])
    df_wr = df_wr_og = pd.read_csv(WRIST_IN_PATH, index_col=[0])

    df_lb = pd.read_csv(LABEL_IN_PATH, index_col=[0])
    df_mt = pd.read_csv(META_IN_PATH)
    df_mn = pd.read_csv(MANIFEST_PATH, index_col=[0]) if os.path.exists(MANIFEST_PATH) else pd.DataFrame()

    # HOUSEKEEPING
    for fname in df_mn.index:
        dir = os.path.join(FOLDER_PATH_OUT, fname)
        if not os.path.exists(dir):
            if verbose: print('- Remove missing file from manifest:', fname)
            df_mn = df_mn.drop(fname)

    period = df_mt['period'][0]
    ahead_by = df_mt['avg_diff'][0]
    waist_ahead = ahead_by < 0
    ahead_by = abs(ahead_by)

    if verbose: print()
    if verbose: print(0, 'SORT by timestamp')
    df_wa = df_wa.sort_values(by=['timestamp(ns)'])
    df_wr = df_wr.sort_values(by=['timestamp(ns)'])

    if verbose: print()
    if ahead_by/period > .5:
        if waist_ahead:
            if verbose: print(1, 'WAIST AHEAD. droping min waist, max wrist')
            df_wa = df_wa.drop(df_wa.index.min())
            df_wr = df_wr.drop(df_wr.index.max())

        else:
            if verbose: print(1, 'WRIST AHEAD. droping min wrist, max waist')
            df_wa = df_wa.drop(df_wa.index.max())
            df_wr = df_wr.drop(df_wr.index.min())
    else:
        if verbose: print(1, f"AVG diff({ahead_by}) is within half period({period})")

    dur_lb = df_lb.index.max() - df_lb.index.min()
    dur_wa = df_wa.index.max() - df_wa.index.min()
    dur_wr = df_wr.index.max() - df_wr.index.min()
    dur_lb /= 1000000000
    dur_wa /= 1000000000
    dur_wr /= 1000000000

    if verbose: print('- Duration label', dur_lb, 's')
    if verbose: print('- Duration waist', dur_wa, 's')
    if verbose: print('- Duration wrist', dur_wr, 's')
    if verbose: print('- combined', df_wa.shape)
    if verbose: print('- waist only', df_wa_og.shape)
    if verbose: print('- wrist only', df_wr_og.shape)

    if verbose: print()
    if verbose: print(2, f"SAMPLE labels from nearest timestamp within period({period}) tolerance")
    df_wa = pd.merge_asof(df_wa, df_lb, on='timestamp(ns)', tolerance=period*1000000, direction='nearest')
    df_wr = pd.merge_asof(df_wr, df_lb, on='timestamp(ns)', tolerance=period*1000000, direction='nearest')
    df_wa_alone = pd.merge_asof(df_wa_og, df_lb, on='timestamp(ns)', tolerance=period*1000000, direction='nearest')
    df_wr_alone = pd.merge_asof(df_wr_og, df_lb, on='timestamp(ns)', tolerance=period*1000000, direction='nearest')
    if verbose: print('- combined', df_wa.shape)
    if verbose: print('- waist only', df_wa_alone.shape)
    if verbose: print('- wrist only', df_wr_alone.shape)

    if verbose: print()
    if verbose: print(3, "ASSUMING that WRIST timestamp == WAIST timestamp")
    df_wa = df_wa.reset_index()
    df_wr = df_wr.reset_index()
    df_comb = df_wa.merge(df_wr.drop('timestamp(ns)', axis=1))
    if verbose: print('- combined', df_comb.shape)

    if verbose: print()
    if verbose: print(4, "DROP NAN")
    df_comb = df_comb[COMB_CSV_HEADERS].dropna()
    df_comb = df_comb.set_index('timestamp(ns)')
    df_wa_alone = df_wa_alone.dropna().set_index('timestamp(ns)')
    df_wr_alone = df_wr_alone.dropna().set_index('timestamp(ns)')

    if verbose: print('- combined', df_comb.shape)
    if verbose: print('- waist only', df_wa_alone.shape)
    if verbose: print('- wrist only', df_wr_alone.shape)

    if verbose: print()
    if verbose: print(5, 'SAVE files to', FOLDER_PATH_OUT)
    if verbose: print()

    open(COMB_OUT_PATH, 'w').close()
    df_comb.to_csv(COMB_OUT_PATH)
    df_wa_alone.to_csv(WAIST_OUT_PATH)
    df_wr_alone.to_csv(WRIST_OUT_PATH)

    tmp = pd.DataFrame().append({
        'filename': filename,
        'period': period,
        'duration_comb': (df_comb.index.max() - df_comb.index.min())/1000000000,
        'duration_waist': (df_wa_alone.index.max() - df_wa_alone.index.min())/1000000000,
        'duration_wrist': (df_wr_alone.index.max() - df_wr_alone.index.min())/1000000000,
        'N_comb': df_comb.shape[0],
        'N_waist': df_wa_alone.shape[0],
        'N_wrist': df_wr_alone.shape[0],
    }, ignore_index=True).set_index('filename')

    if verbose: print()
    if verbose: print('* INPUT metadata')
    if verbose: print(df_mt,'\n')
    if verbose: print('* OUTPUT metadata')
    if verbose: print(df_mn)
    df_mn = df_mn.append(tmp)
    df_mn = df_mn[~df_mn.index.duplicated(keep='last')]
    df_mn.to_csv(MANIFEST_PATH)

def main(files, dataset):
    first = True
    for i, file in enumerate(files):
        try:
            combine(file, dataset, False)
        except Exception as e:
            print(e)

if __name__ == "__main__":

    HAR_files = [
        # 'stairs_brian_1',
        # 'stairs_brian_2',
        'stairs_brian_3',
        'stairs_brian_4',
        'walking_brian_1',
        'walking_brian_2',
        'standing_brian_1',
        'stationary_brian_2',
        'stationary_brian_3',
        'walk_circle_brian_anti',
        'walk_circle_brian_clock',
    ] # walking, stationary, etc
    print(HAR_files)
    if HAR_files:
        HAR_dataet = 'HAR'
        main(HAR_files, HAR_dataet)

    FD_files = [
        # 'leaning_brian_1',
        'falling_brian_2',
        'falling_brian_3',
        'falling_brian_4',
        'falling_brian_5',
        'falling_brian_7',
    ]
    if FD_files:
        FD_dataset = 'falldet'
        main(FD_files, FD_dataset)
