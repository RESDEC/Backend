import sys

from surprise import Dataset
from surprise import Reader, BaselineOnly
from surprise import evaluate, print_perf

from src.servicios import util
from src.config import configuration


# Funcion para ejecutar el Base Only
def base_only():
    print('Algoritmo Baseline Only...')
    print('Que data desea utilizar?')
    print('(1) Android')
    print('(2) WordPress')
    data_utilizar = input()

    # Funcion de encoding para no tener error de lectura del archivo.
    reload(sys)
    sys.setdefaultencoding('utf8')
    sys.setdefaultencoding('latin-1')

    if data_utilizar == 1:
        file_path = configuration.FILE_PATH_ANDROID
        reader = Reader(line_format='user item rating', sep='\t')
    else:
        file_path = configuration.FILE_PATH_WORDPRESS
        file_path_corregido = configuration.FILE_PATH_WORDPRESS_CORREGIDA
        util.corregir_csv(file_path, file_path_corregido, sep="|")
        reader = Reader(line_format='user item rating', sep='|')

    data = Dataset.load_from_file(file_path_corregido, reader=reader)
    data.split(n_folds=10)

    algo = BaselineOnly()

    perf = evaluate(algo, data, measures=['RMSE', 'MAE'])
    print_perf(perf)


base_only()
