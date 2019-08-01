# coding=utf-8

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def convert_data_tf_idf(data_frame=None, item_col="item", features_filter=None):
    if not features_filter:
        print('\nReformatting Data >> No filters.')
    else:
        print('\nReformatting Data >> Tags Filter:')
        for item in features_filter:
            print('Reformatting Data >> - ' + item)

    items = list(data_frame[item_col].unique())

    arr = []
    for item in items:
        item_features = ''
        feature_exists = False

        for i, f in data_frame.values:
            if i == item:
                item_features += f + ' '
                for f in features_filter:
                    if f in f:
                        feature_exists = True
                        break
        if not features_filter:
            arr.append([item_features, item])
        else:
            if feature_exists:
                arr.append([item_features, item])

    data_frame = pd.DataFrame(arr)
    return data_frame


def find_similar(tfidf_matrix, index, top_n=2):
    cosine_similarities = linear_kernel(tfidf_matrix[index:index + 1], tfidf_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != index]
    return [(index, cosine_similarities[index]) for index in related_docs_indices][0:top_n]


class TransitionComponentsBasedFeatures:
    def __init__(self, file_path=None, delimiter="|", item_evaluated=None, number_recommendations=5):
        self.file_path = file_path
        self.delimiter = delimiter
        self.item_evaluated = item_evaluated
        self.number_recommendations = number_recommendations

    def tf_idf_cosine_similarity(self, item_col="item", features_col="features"):
        print("calculating tf idf cosine similarity... File Rating: " + self.file_path)
        print("calculating tf idf cosine similarity... Item to Evaluate: " + self.item_evaluated)
        print("calculating tf idf cosine similarity... Number of recommendations: " + str(self.number_recommendations))

        df = pd.read_csv(self.file_path, encoding='latin-1', sep=self.delimiter)

        # Features of the item.
        features = df[df[item_col] == str(self.item_evaluated)][features_col]
        features_filter = list(features)

        data_frame_converted = convert_data_tf_idf(data_frame=df,
                                                   item_col=item_col,
                                                   features_filter=features_filter)

        corpus = []  # Matrix to get all the values from the CSV
        df = pd.DataFrame(data_frame_converted)
        docs = list(df[0])
        titles = list(df[1])

        i = 0
        index_item = 0
        while i < titles.__len__():
            if titles[i] and docs[i]:
                corpus.append((titles[i], docs[i]))
                if titles[i] == self.item_evaluated:
                    index_item = i
                    print("\nTransition Component Based Features >> Item to evaluated: " + str(titles[i]))
                i += 1

        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform([content for file, content in corpus])

        dict_recommendation = {}
        print("\nTransition Component Based Features >> Recommended items by TIF-IDF and Cosine of similarity:")
        i = 0
        for index, score in find_similar(tfidf_matrix, index_item, int(self.number_recommendations)):
            i += 1
            dict_recommendation[i] = corpus[index][0]
            print("- ", score, corpus[index][0])

        return dict_recommendation
