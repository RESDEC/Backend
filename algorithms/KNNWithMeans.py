# coding=utf-8
import sys

from surprise import Dataset
from surprise import Reader, KNNWithMeans
from surprise import evaluate, print_perf

from src.config import configuration


def knn_with_means():
    print('Algoritmo Baseline Only...')
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
    data.split(n_folds=10)

    """Segmento que utiliza KNN para el analisis:
        'k' Es el numero maximo de vecinos a tomar en cuenta para la agregacion
        'min_k' El numero minimo de vecinos a tomar en cuenta para la agregacion.
            Si no hay suficientes vecinos,la predicción se establece en la media global de todas las calificaciones
        'sim_options' son las opciones de similitud que utiliza el knn"""

    k = 40
    min_k = 1
    sim_options = {'name': 'pearson_baseline',
                   'user_based': 0  # no shrinkage
                   }

    algo = KNNWithMeans(k=k, min_k=k, sim_options=sim_options)

    perf = evaluate(algo, data, measures=['RMSE', 'MAE'])
    print_perf(perf)

knn_with_means()