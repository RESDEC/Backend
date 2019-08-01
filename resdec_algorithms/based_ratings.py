import sys
import numpy as np
import pandas as pd

from collections import defaultdict

from surprise import Dataset
from surprise import Reader, SVD, KNNBaseline
import imp


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
    for uid, user_ratings in list(top_n.items()):
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


def top_cosine_similarity(data, item_id, top_n=10):
    index = item_id - 1  # Movie id starts from 1
    item_row = data[index, :]
    magnitude = np.sqrt(np.einsum('ij, ij -> i', data, data))
    similarity = np.dot(item_row, data.T) / (magnitude[index] * magnitude)
    sort_indexes = np.argsort(-similarity)
    return sort_indexes[:top_n]


class TransitionComponentsBasedFeatures:
    def __init__(self, file_path, delimiter, item_evaluated, number_recommendations):
        self.file_path = file_path
        self.delimiter = delimiter
        self.item_evaluated = item_evaluated
        self.number_recommendations = number_recommendations

        imp.reload(sys)
        sys.setdefaultencoding('latin1')

    def svd(self):
        print(("calculating svd... File Rating: " + self.file_path))
        print(("calculating svd... Item to Evaluate: " + self.item_evaluated))
        print(("calculating svd... Number of recommendations: " + str(self.number_recommendations)))

        # Read the files with pandas
        df = pd.read_csv(self.file_path, engine='python',
                         names=['item', 'user', 'rating'],
                         delimiter=str(self.delimiter), header=None)

        """Preparing data with indexes, items and users"""

        # Unique items and users
        unique_items = pd.unique(df.item.values)
        unique_users = pd.unique(df.user.values)

        # Dictionaries
        arr_items_index = []
        arr_items_names = []
        dict_items = {}
        x = 0
        for i in unique_items:
            x += 1
            arr_items_index.append(x)
            arr_items_names.append(i)
            dict_items[x] = i

        arr_users_index = []
        arr_users_names = []
        dict_users = {}
        y = 0
        for u in unique_users:
            y += 1
            arr_users_index.append(y)
            arr_users_names.append(u)
            dict_users[y] = u

        dict_id_items = {'item_id': arr_items_index,
                         'item_name': arr_items_names}
        dict_id_users = {'user_id': arr_users_index,
                         'user_name': arr_users_names}

        # DataFrames Items and Users with id's
        df_items = pd.DataFrame(data=dict_id_items)
        df_users = pd.DataFrame(data=dict_id_users)

        # Merging
        merged_items = pd.merge(df, df_items, left_on='item', right_on='item_name', how='inner')
        merged_all = pd.merge(merged_items, df_users, left_on='user', right_on='user_name', how='inner')

        print(("calculating svd... Total items to evaluated: " + str(np.max(merged_all.item_id.values))))
        print(("calculating svd... Total users to evaluated: " + str(np.max(merged_all.user_id.values))))

        # Create the ratings matrix of shape (M x U) with rows as items and columns as users
        ratings_mat = np.ndarray(
            shape=(np.max(merged_all.item_id.values), np.max(merged_all.user_id.values)),
            dtype=np.uint8
        )
        ratings_mat[merged_all.item_id.values - 1,
                    merged_all.user_id.values - 1] = merged_all.rating.values

        # Normalise matrix (subtract mean off)
        normalised_mat = ratings_mat - np.asarray([(np.mean(ratings_mat, 1))]).T

        # Compute SVD
        a = normalised_mat.T / np.sqrt(ratings_mat.shape[0] - 1)
        U, S, V = np.linalg.svd(a)

        # Select K principal components to represent the items, a items to find recommendations
        # and print the top_n results
        k = 50
        top_n = int(self.number_recommendations) + 1
        item = df_items.loc[df_items['item_name'] == self.item_evaluated].item_id.values[0]

        sliced = V.T[:, :k]  # representative data
        indexes = top_cosine_similarity(sliced, item, top_n)

        # Return the result
        dictionary_svd = {}
        x = 0
        for i in indexes + 1:
            item_str = df_items.loc[df_items['item_id'] == i].item_name.values[0]
            if item_str != self.item_evaluated:
                print(item_str)
                x += 1
                dictionary_svd[x] = item_str

        return dictionary_svd

    def knn_basic(self):
        print(("calculating knn basic... File Rating: " + self.file_path))
        print(("calculating knn basic... Item to Evaluate: " + self.item_evaluated))
        print(("calculating knn basic... Number of recommendations: " + str(self.number_recommendations)))

        # Reader
        reader = Reader(line_format='item user rating', sep=self.delimiter, skip_lines=1)

        # Dataset
        data = Dataset.load_from_file(self.file_path, reader=reader)

        trainset = data.build_full_trainset()
        sim_options = {'name': 'pearson_baseline',
                       'user_based': True}
        algo = KNNBaseline(sim_options=sim_options)
        algo.fit(trainset)

        item_inner_id = algo.trainset.to_inner_iid(self.item_evaluated)

        item_neighbors = algo.get_neighbors(item_inner_id, k=int(self.number_recommendations))

        item_neighbors = (algo.trainset.to_raw_iid(inner_id) for inner_id in item_neighbors)

        dictionary_neighbors = {}
        i = 0
        for item in item_neighbors:
            i += 1
            dictionary_neighbors[i] = item

        return dictionary_neighbors

    def knn_centered(self):
        print(("calculating knn centered... File Rating: " + self.file_path))
        print(("calculating knn centered... Item to Evaluate: " + self.item_evaluated))
        print(("calculating knn centered... Number of recommendations: " + str(self.number_recommendations)))

        # Reader
        reader = Reader(line_format='item user rating', sep=self.delimiter, skip_lines=1)

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
            print(("- " + item))

        return dictionary_neighbors
