import sys

from surprise import Dataset
from surprise import Reader, SVDpp
from surprise import evaluate, print_perf

from src.config import configuration


def svd_pp():
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

    algo = SVDpp()

    perf = evaluate(algo, data, measures=['RMSE', 'MAE'])
    print_perf(perf)

svd_pp()
