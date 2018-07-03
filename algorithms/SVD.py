import sys

from surprise import Dataset
from surprise import Reader, SVD
from surprise import evaluate, print_perf


def svd(file_path=None, sep=","):
    print('Using SVD algorithm...')

    # Funcion de encoding para no tener error de lectura del archivo.
    reload(sys)
    sys.setdefaultencoding('utf8')

    reader = Reader(line_format='user item rating', sep=sep)

    # Dataset
    data = Dataset.load_from_file(file_path, reader=reader)
    data.split(n_folds=10)

    algo = SVD()

    perf = evaluate(algo, data, measures=['RMSE', 'MAE'])
    print_perf(perf)
