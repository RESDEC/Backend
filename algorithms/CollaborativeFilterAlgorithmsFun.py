# coding=utf-8

from __future__ import print_function

# from IPython.config.application import catch_config_error
from contextlib import closing
from datetime import date, datetime
from multiprocessing import Pool
from surprise import Dataset
from surprise import Reader, NormalPredictor, SVD, SVDpp, BaselineOnly, KNNBasic, KNNWithMeans, KNNBaseline, NMF, \
    SlopeOne, CoClustering
from surprise import accuracy
from surprise import model_selection
from surprise.model_selection import train_test_split, cross_validate, ShuffleSplit

from ResdecSolution.settings import BASE_DIR

import numpy as np
import pandas as pd


MESSAGE = ""


def print_perf(performances, file, n_folds):
    # dict = {'mae':0.0, 'rmse': 0.0, 'time': 0.0}
    # for ex in performances:
    #    for key in ex:
    #        dict[key] += ex[key] / n_folds

    file.write(str(n_folds) + ',' + str(performances))


def testAlgor(alg, data, n_folds, rep):
    pkf = ShuffleSplit(n_splits=rep, test_size=1 / float(n_folds), train_size=None, random_state=rep, shuffle=True)
    dict = cross_validate(alg, data, cv=pkf, n_jobs=n_folds, verbose=False)
    result = {'rmse': dict['test_rmse'],
              'mae': dict['test_mae']}  # , 'fit_time': dict['fit_time'], 'test_time': dict['test_time']
    return result


def surprise_algorithms_print_perf((rep, n_folds)):
    # nan = {'rmse': 'NaN', 'mae': 'NaN', 'fit_time': 'NaN', 'test_time': 'NaN'}
    # file_path = '../split/rep' + str(rep) + '/folds' + str(n_folds)
    # i = 1
    # perf = list()
    # perf_baseline_only = list()
    perf_svd = list()
    # perf_svdpp = list()
    # perf_nmf = list()
    # perf_slope = list()
    # perf_coclustering = list()
    perf_knn_basic = list()
    perf_knn_means = list()
    # perf_knn_baseline = list()
    # lista = list()
    # for fold in range(1, n_folds + 1):
    #    reader = Reader(line_format='user item rating', sep=',')
    #    training_file = file_path + '/training' + str(fold) + '.csv'
    #    test_file = file_path + '/test' + str(fold) + '.csv'
    #    lista.append((training_file, test_file))
    # print(str(lista))

    interactions_df = pd.read_csv(BASE_DIR + '/static/data/raw/wordpress_ext.csv')
    users_interactions_count_df = interactions_df.groupby(['widget', 'user']).size().groupby('user').size()
    users_with_enought_interactions_df = users_interactions_count_df[users_interactions_count_df >= 5].reset_index()[
        ['user']]

    interactions_from_selected_users_df = interactions_df.merge(users_with_enought_interactions_df,
                                                                how='right',
                                                                left_on='user',
                                                                right_on='user')

    interactions_full_df = interactions_from_selected_users_df.groupby(['user', 'widget'])['rating'].sum().reset_index()
    reader = Reader(line_format='user item rating', sep=',', skip_lines=1)
    data = Dataset.load_from_df(interactions_full_df, reader)

    sim_options = {'name': 'pearson_baseline', 'user_based': True}
    # K-NN (usuarios)
    print('KNN Basico')

    algo = KNNBasic(k=5, sim_options=sim_options)
    perf_knn_basic.append(testAlgor(algo, data, n_folds, rep))

    sim_options = {'name': 'pearson_baseline',
                   'user_based': False  # compute  similarities between items
                   }
    print('KNN Centrado')
    algo = KNNBasic(k=5, sim_options=sim_options)
    perf_knn_means.append(testAlgor(algo, data, n_folds, rep))

    # print('KNN Baseline')

    # algo = KNNBaseline(k=5, sim_options = sim_options)

    # try:
    #    perf_knn_baseline.append(testAlgor(algo, data, n_folds, rep))
    # except:
    #    perf_knn_baseline.append(nan)

    # BaselineOnly
    # print('Predictor normal')
    # algo = NormalPredictor()
    # try:
    #    perf.append(testAlgor(algo, data, n_folds, rep))
    # except:
    #    perf.append('NaN')

    # BaselineOnly
    # print('Baseline')
    # algo = BaselineOnly()
    # try:
    #    perf_baseline_only.append(testAlgor(algo, data, n_folds, rep))
    # except:
    #    perf_baseline_only.append(nan)

    # SVD
    print('SVD')
    algo = SVD(biased=False)
    perf_svd.append(testAlgor(algo, data, n_folds, rep))

    # SVDpp
    # print('SVD++')
    # algo = SVDpp()
    # try:
    #    perf_svdpp.append(testAlgor(algo, data, n_folds, rep))
    # except:
    #    perf_svdpp.append(nan)

    # NMF
    # print('NMF')
    # algo = NMF()
    # try:
    #    perf_nmf.append(testAlgor(algo, data, n_folds, rep))
    # except:
    #    perf_nmf.append(nan)

    # Slope One
    # print('Slope One')
    # algo = SlopeOne()
    # try:
    #    perf_slope.append(testAlgor(algo, data, n_folds, rep))
    # except:
    #    perf_slope.append(nan)
    # CoClustering        
    # print('coclustering')
    # algo = CoClustering()
    # try:
    #    perf_coclustering.append(testAlgor(algo, data, n_folds, rep))
    # except:
    #    perf_coclustering.append(nan)

    with open(str(rep) + '-' + str(n_folds) + '.csv', 'w+') as f:
        # f.write('Normal predictor,')
        # print_perf(perf, f, n_folds)
        # f.write('\n')
        # f.write('Baseline,')
        # print_perf(perf_baseline_only, f, n_folds)
        # f.write('\n')
        f.write('SVD,')
        print_perf(perf_svd, f, n_folds)
        f.write('\n')
        # f.write('SVDpp,')
        # print_perf(perf_svdpp, f, n_folds)
        # f.write('\n')
        # f.write('NMF,')
        # print_perf(perf_nmf, f, n_folds)
        # f.write('\n')
        # f.write('SlopeOne,')
        # print_perf(perf_slope, f, n_folds)
        # f.write('\n')
        # f.write('Coclustering,')
        # print_perf(perf_coclustering, f, n_folds)
        # f.write('\n')
        f.write('KnnBasic,')
        print_perf(perf_knn_basic, f, n_folds)
        f.write('\n')
        f.write('KnnMeans,')
        print_perf(perf_knn_means, f, n_folds)
        f.write('\n')
        # f.write('KnnBaseline,')
        # print_perf(perf_knn_baseline, f, n_folds)
        # f.write('\n')
        f.close()


def start():
    init = datetime.utcnow()
    with closing(Pool(processes=5)) as pool:
        pool.map(surprise_algorithms_print_perf, [
            # (1, 3), (1, 5), (1, 7)])#, #(1, 10),
            # (2, 3), (2, 5), (2, 7), #(2, 10),
            # (3, 3), (3, 5), (3, 7), #(3, 10),
            # (4, 3), (4, 5), (4, 7), #(4, 10),
            (5, 3), (5, 5), (5, 7)])
        pool.terminate()
    print(init)
    print(datetime.utcnow())

    return "Hello World!!"
