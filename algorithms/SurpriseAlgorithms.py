# coding=utf-8
from __future__ import print_function
from __future__ import print_function

from surprise import Dataset
from surprise import Reader, NormalPredictor, SVD, SVDpp, BaselineOnly, KNNBasic, KNNWithMeans, KNNBaseline, NMF, SlopeOne, CoClustering
from surprise import evaluate, print_perf

from src.config import configuration

import sys


# Imprime los resultados finales de todos los algorithmos utilizados
def surprise_algorithms_print_perf():
    print('Surprise Algorithms (Tabla de resultados finales)...')
    print('Que data desea utilizar?')
    print('(1) Android')
    print('(2) WordPress')
    data_utilizar = input()

    # Funcion de encoding para no tener error de lectura del archivo.
    reload(sys)
    sys.setdefaultencoding('utf8')

    if data_utilizar == 1:
        file_path = configuration.FILE_PATH_ANDROID
        reader = Reader(line_format='user item rating', sep='\t')
    else:
        file_path = configuration.FILE_PATH_WORDPRESS
        reader = Reader(line_format='user item rating', sep=',')

    # Dataset
    data = Dataset.load_from_file(file_path, reader=reader)
    data.split(n_folds=5)

    # BaselineOnly
    algo_normal_predictor = NormalPredictor()
    perf_normal_predictor = evaluate(algo_normal_predictor, data, measures=['RMSE', 'MAE'], verbose=False)

    # SVD
    algo_svd = SVD()
    perf_svd = evaluate(algo_svd, data, measures=['RMSE', 'MAE'], verbose=False)

    # BaselineOnly
    algo_baseline_only = BaselineOnly()
    perf_baseline_only = evaluate(algo_baseline_only, data, measures=['RMSE', 'MAE'], verbose=False)

    # SVDpp
    algo_svdpp = SVDpp()
    perf_svdpp = evaluate(algo_svdpp, data, measures=['RMSE', 'MAE'], verbose=False)

    # NMF
    algo_nmf = NMF()
    perf_nmf = evaluate(algo_nmf, data, measures=['RMSE', 'MAE'], verbose=False)

    # SlopeOne
    algo_slope_one = SlopeOne()
    perf_slope_one = evaluate(algo_slope_one, data, measures=['RMSE', 'MAE'], verbose=False)

    # CoClustering
    algo_coclustering = CoClustering()
    perf_coclustering = evaluate(algo_coclustering, data, measures=['RMSE', 'MAE'], verbose=False)

    """Segmento que utiliza KNN para el analisis:
        'k' Es el numero maximo de vecinos a tomar en cuenta para la agregacion
        'min_k' El numero minimo de vecinos a tomar en cuenta para la agregacion.
            Si no hay suficientes vecinos,la predicción se establece en la media global de todas las calificaciones
        'sim_options' son las opciones de similitud que utiliza el knn
        'bsl_options' configuracion de las estimaciones de base"""

    k = 40
    min_k = 1
    sim_options = {'name': 'pearson_baseline',
                   'user_based': 0  # no shrinkage
                   }
    bsl_options = {'method': 'als',
                   'n_epochs': 5,
                   'reg_u': 12,
                   'reg_i': 5
                   }

    algo_knn_basic = KNNBasic(k=k, min_k=k, sim_options=sim_options)
    perf_knn_basic = evaluate(algo_knn_basic, data, measures=['RMSE', 'MAE'], verbose=False)

    algo_knn_with_means = KNNWithMeans(k=k, min_k=k, sim_options=sim_options)
    perf_knn_with_means = evaluate(algo_knn_with_means, data, measures=['RMSE', 'MAE'], verbose=False)

    algo_knn_base_line = KNNBaseline(k=k, min_k=k, sim_options=sim_options, bsl_options=bsl_options)
    perf_knn_base_line = evaluate(algo_knn_base_line, data, measures=['RMSE', 'MAE'], verbose=False)

    """Imprimiendo resultados de los algoritmos"""
    print('')
    print('Printing results from algorithms...')
    print('- Normal predictor')
    print_perf(perf_normal_predictor)
    print('')
    print('- Normal SVD')
    print_perf(perf_svd)
    print('')
    print('- Normal Baseline Only')
    print_perf(perf_baseline_only)
    print('')
    print('- Normal SVD++')
    print_perf(perf_svdpp)
    print('')
    print('- Normal NMF')
    print_perf(perf_nmf)
    print('')
    print('- Normal Slope One')
    print_perf(perf_slope_one)
    print('')
    print('- Normal Co-Clustering')
    print_perf(perf_coclustering)
    print('')
    print('- Normal KNN Basic')
    print_perf(perf_knn_basic)
    print('')
    print('- Normal KNN With Means')
    print_perf(perf_knn_with_means)
    print('')
    print('- Normal KNN Base Line')
    print_perf(perf_knn_base_line)

surprise_algorithms_print_perf()
