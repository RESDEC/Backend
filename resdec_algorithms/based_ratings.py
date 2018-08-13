import sys, io

from collections import defaultdict

from surprise import Dataset
from surprise import Reader, SVD, KNNBaseline


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


class TransitionComponentsBasedFeatures:
    def __init__(self, file_path, delimiter, item_evaluated, number_recommendations):
        self.file_path = file_path
        self.delimiter = delimiter
        self.item_evaluated = item_evaluated
        self.number_recommendations = number_recommendations

        reload(sys)
        sys.setdefaultencoding('latin1')

    def svd(self):
        # Reader
        reader = Reader(line_format='user item rating', sep=self.delimiter, skip_lines=1)

        # Dataset
        data = Dataset.load_from_file(self.file_path, reader=reader)

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

    def knn_basic(self):
        print("calculating knn basic... File Rating: " + self.file_path)
        print("calculating knn basic... Item to Evaluate: " + self.item_evaluated)
        print("calculating knn basic... Number of recommendations: " + str(self.number_recommendations))

        # Reader
        reader = Reader(line_format='user item rating', sep=self.delimiter, skip_lines=1)

        # Dataset
        data = Dataset.load_from_file(self.file_path, reader=reader)

        trainset = data.build_full_trainset()
        sim_options = {'name': 'pearson_baseline',
                       'user_based': True}
        algo = KNNBaseline(sim_options=sim_options)
        algo.fit(trainset)

        item_inner_id = algo.trainset.to_inner_iid(self.item_evaluated)

        item_neighbors = algo.get_neighbors(item_inner_id, k=5)

        item_neighbors = (algo.trainset.to_raw_iid(inner_id) for inner_id in item_neighbors)

        dictionary_neighbors = {}
        i = 0
        for item in item_neighbors:
            i += 1
            dictionary_neighbors[i] = item

        return dictionary_neighbors

    def knn_centered(self):
        print("calculating knn centered... File Rating: " + self.file_path)
        print("calculating knn centered... Item to Evaluate: " + self.item_evaluated)
        print("calculating knn centered... Number of recommendations: " + str(self.number_recommendations))

        # Reader
        reader = Reader(line_format='user item rating', sep=self.delimiter, skip_lines=1)

        # Dataset
        data = Dataset.load_from_file(self.file_path, reader=reader)

        trainset = data.build_full_trainset()
        sim_options = {'name': 'pearson_baseline',
                       'user_based': False}
        algo = KNNBaseline(sim_options=sim_options)
        algo.fit(trainset)

        item_inner_id = algo.trainset.to_inner_iid(self.item_evaluated)

        item_neighbors = algo.get_neighbors(item_inner_id, k=int(self.number_recommendations))

        item_neighbors = (algo.trainset.to_raw_iid(inner_id) for inner_id in item_neighbors)

        dictionary_neighbors = {}
        print("\nTransition Component Based Ratings >> Recommended items by KNN Centered:")
        i = 0
        for item in item_neighbors:
            i += 1
            dictionary_neighbors[i] = item
            print("- " + item)

        return dictionary_neighbors
