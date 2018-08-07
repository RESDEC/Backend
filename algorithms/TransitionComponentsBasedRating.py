import sys

from collections import defaultdict

from surprise import Dataset
from surprise import Reader, SVD, KNNBasic
from surprise.model_selection import cross_validate


def get_top_n(predictions, n=10):
    """Return the top-N recommendation for each user from a set of predictions.

        Args:
            predictions(list of Prediction objects): The list of predictions, as
                returned by the test method of an algorithm.
            n(int): The number of recommendation to output for each user. Default
                is 10.

        Returns:
        A dict where keys are user (raw) ids and values are lists of tuples:
            [(raw item id, rating estimation), ...] of size n.
        """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


def svd(file_path=None, sep=","):
    print('Using SVD algorithm...')

    reload(sys)
    sys.setdefaultencoding('latin1')

    # Reader
    reader = Reader(line_format='user item rating', sep=sep, skip_lines=1)

    # Dataset
    data = Dataset.load_from_file(file_path, reader=reader)

    # Creating the trainset
    trainset = data.build_full_trainset()

    algo = SVD()
    algo.fit(trainset)

    # Than predict ratings for all pairs (u, i) that are NOT in the training set.
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    top_n = get_top_n(predictions, n=5)

    # Print the recommended items for each user
    # for uid, user_ratings in top_n.items():
    #     print(uid, [iid for (iid, _) in user_ratings])


def knn_basic(file_path=None, sep=","):
    print('Using KNN Basic algorithm...')

    reader = Reader(line_format='user item rating', sep=sep, skip_lines=1)

    reload(sys)
    sys.setdefaultencoding('latin1')

    # Dataset
    data = Dataset.load_from_file(file_path, reader=reader)
    data.split(n_folds=5)

    sim_options = {'name': 'pearson_baseline',
                   'user_based': True
                   }

    algo = KNNBasic(k=5, sim_options=sim_options, verbose=True)

    # Run 5-fold cross-validation and print results
    cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)


def knn_centered(file_path=None, sep=","):
    print('Using KNN Centered algorithm...')

    reader = Reader(line_format='user item rating', sep=sep, skip_lines=1)

    reload(sys)
    sys.setdefaultencoding('latin1')

    # Dataset
    data = Dataset.load_from_file(file_path, reader=reader)
    data.split(n_folds=10)

    sim_options = {'name': 'pearson_baseline',
                   'user_based': False
                   }

    algo = KNNBasic(k=5, sim_options=sim_options)

    # Run 5-fold cross-validation and print results
    cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
