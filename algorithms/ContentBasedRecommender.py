import numpy as np
import scipy
import pandas as pd
import math
import random
import sklearn
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
import matplotlib.pyplot as plt

# In[2]
articles_df = pd.read_csv('../data/corregido_plugins.csv')
print('')
print('Out[2]:')
print(articles_df.head(5))

# In[3]. Csv con los usuarios, widget sy ratings
interactions_df = pd.read_csv('../data/corregido_ratings.csv', sep='|')
print('')
print('Out[3]:')
print(interactions_df.head(10))

# In[5]
print('')
print('Out[6]:')
users_interactions_count_df = interactions_df.groupby(['widget', 'user']).size().groupby('user').size()
content_interactions_count_df = interactions_df.groupby(['widget', 'user']).size().groupby('widget').size()
print('# users: %d' % len(users_interactions_count_df))
print('# contents: %d' % len(content_interactions_count_df))
users_with_enought_interactions_df = users_interactions_count_df[users_interactions_count_df >= 5].reset_index()[
    ['user']]
print('# users with at least 5 interactions: %d' % len(users_with_enought_interactions_df))

# In[6]
print('')
print('Out[7]:')
print('# of interactions: %d' % len(interactions_df))
interactions_from_selected_users_df = interactions_df.merge(users_with_enought_interactions_df,
                                                            how='right',
                                                            left_on='user',
                                                            right_on='user')
print('# of interactions from users with at least 5 interactions: %d' % len(interactions_from_selected_users_df))


# In[7]
def smooth_user_preference(x):
    return math.log(1 + x, 2)


interactions_full_df = interactions_from_selected_users_df.groupby(['user', 'widget'])['rating'].sum().apply(
    smooth_user_preference).reset_index()
print('# of unique user/item interactions: %d' % len(interactions_full_df))
print(interactions_full_df.head(10))

# In[8]
interactions_train_df, interactions_test_df = train_test_split(interactions_full_df,
                                                               stratify=interactions_full_df['user'],
                                                               test_size=0.20,
                                                               random_state=42)
print('')
print('Out[8]:')
print('# interactions on Train set: %d' % len(interactions_train_df))
print('# interactions on Test set: %d' % len(interactions_test_df))

# In[9]
interactions_full_indexed_df = interactions_full_df.set_index('user')
interactions_train_indexed_df = interactions_train_df.set_index('user')
interactions_test_indexed_df = interactions_test_df.set_index('user')


# In[10]
def get_items_interacted(person_id, interactions_df):
    interacted_items = interactions_df.loc[person_id]['widget']
    return set(interacted_items if type(interacted_items) == pd.Series else [interacted_items])


# In[11]
EVAL_RANDOM_SAMPLE_NON_INTERACTED_ITEMS = 100


class ModelEvaluator:
    def __init__(self):
        pass

    def get_not_interacted_items_sample(self, person_id, sample_size, seed=42):
        interacted_items = get_items_interacted(person_id, interactions_full_indexed_df)
        all_items = set(articles_df['widget'])
        non_interacted_items = all_items - interacted_items

        random.seed(seed)
        non_interacted_items_sample = random.sample(non_interacted_items, sample_size)
        return set(non_interacted_items_sample)

    def _verify_hit_top_n(self, item_id, recommended_items, topn):
        try:
            index = next(i for i, c in enumerate(recommended_items) if c == item_id)
        except:
            index = -1
        hit = int(index in range(0, topn))
        return hit, index

    def evaluate_model_for_user(self, model, person_id):
        interacted_values_testset = interactions_test_indexed_df.loc[person_id]
        if type(interacted_values_testset['widget']) == pd.Series:
            person_interacted_items_testset = set(interacted_values_testset['widget'])
        else:
            # person_interacted_items_testset = set([int(interacted_values_testset['widget'])])
            # Modificacion por problemas de int()
            person_interacted_items_testset = set([int(hash(interacted_values_testset['widget']))])
        interacted_items_count_testset = len(person_interacted_items_testset)

        person_recs_df = model.recommend_items(person_id,
                                               items_to_ignore=get_items_interacted(person_id,
                                                                                    interactions_train_indexed_df),
                                               topn=10000000000)

        hits_at_5_count = 0
        hits_at_10_count = 0
        for item_id in person_interacted_items_testset:
            # Insercion de codigo para poder realizar el hascode del item id en numerico
            item_id_hs = hash(item_id)

            non_interacted_items_sample = self.get_not_interacted_items_sample(person_id,
                                                                               sample_size=EVAL_RANDOM_SAMPLE_NON_INTERACTED_ITEMS,
                                                                               seed=item_id_hs % (2 ** 42))

            items_to_filter_recs = non_interacted_items_sample.union(set([item_id]))

            valid_recs_df = person_recs_df[person_recs_df['widget'].isin(items_to_filter_recs)]
            valid_recs = valid_recs_df['widget'].values

            hit_at_5, index_at_5 = self._verify_hit_top_n(item_id, valid_recs, 5)
            hits_at_5_count += hit_at_5
            hit_at_10, index_at_10 = self._verify_hit_top_n(item_id, valid_recs, 10)
            hits_at_10_count += hit_at_10

        recall_at_5 = hits_at_5_count / float(interacted_items_count_testset)
        recall_at_10 = hits_at_10_count / float(interacted_items_count_testset)

        person_metrics = {'hits@5_count': hits_at_5_count,
                          'hits@10_count': hits_at_10_count,
                          'interacted_count': interacted_items_count_testset,
                          'recall@5': recall_at_5,
                          'recall@10': recall_at_10}
        return person_metrics

    def evaluate_model(self, model):
        # print('Running evaluation for users')
        people_metrics = []
        for idx, person_id in enumerate(list(interactions_test_indexed_df.index.unique().values)):
            # if idx % 100 == 0 and idx > 0:
            #    print('%d users processed' % idx)
            person_metrics = self.evaluate_model_for_user(model, person_id)
            person_metrics['_person_id'] = person_id
            people_metrics.append(person_metrics)
        print('%d users processed' % idx)

        detailed_results_df = pd.DataFrame(people_metrics) \
            .sort_values('interacted_count', ascending=False)

        global_recall_at_5 = detailed_results_df['hits@5_count'].sum() / float(
            detailed_results_df['interacted_count'].sum())
        global_recall_at_10 = detailed_results_df['hits@10_count'].sum() / float(
            detailed_results_df['interacted_count'].sum())

        global_metrics = {'modelName': model.get_model_name(),
                          'recall@5': global_recall_at_5,
                          'recall@10': global_recall_at_10}
        return global_metrics, detailed_results_df


model_evaluator = ModelEvaluator()

# In[12]
item_popularity_df = interactions_full_df.groupby('widget')['rating'].sum().sort_values(ascending=False).reset_index()
print('')
print('Out[12]')
print(item_popularity_df.head(10))


# Content-Based Filtering model
# In[15]
stopwords_list = stopwords.words('english')
vectorizer = TfidfVectorizer(analyzer='word',
                             ngram_range=(1, 1),
                             min_df=0.003,
                             max_df=0.5,
                             max_features=5000,
                             stop_words=stopwords_list)

item_ids = articles_df['widget'].tolist()
tfidf_matrix = vectorizer.fit_transform(articles_df['tag'])
tfidf_feature_names = vectorizer.get_feature_names()
print('')
print('Out[15]')
print(tfidf_matrix)


# In[16]
def get_item_profile(item_id):
    idx = item_ids.index(item_id)
    item_profile = tfidf_matrix[idx:idx + 1]
    return item_profile


def get_item_profiles(ids):
    item_profiles_list = [get_item_profile(x) for x in ids]
    item_profiles = scipy.sparse.vstack(item_profiles_list)
    return item_profiles


def build_users_profile(user, interactions_indexed_df):
    interactions_person_df = interactions_indexed_df.loc[user]
    user_item_profiles = get_item_profiles(interactions_person_df['widget'])

    user_item_strengths = np.array(interactions_person_df['rating']).reshape(-1, 1)
    user_item_strengths_weighted_avg = \
        np.sum(user_item_profiles.multiply(user_item_strengths), axis=0) / np.sum(user_item_strengths)
    user_profile_norm = sklearn.preprocessing.normalize(user_item_strengths_weighted_avg)
    return user_profile_norm


def build_users_profiles():
    interactions_indexed_df = interactions_full_df[
        interactions_full_df['widget'].isin(articles_df['widget'])].set_index('user')
    user_profiles = {}
    for user in interactions_indexed_df.index.unique():
        user_profiles[user] = build_users_profile(user, interactions_indexed_df)
    return user_profiles


# In[17]
user_profiles = build_users_profiles()
print('')
print('Out[17]')
print(len(user_profiles))

# In[18]
myprofile = user_profiles['.gabriel.']
print('')
print('Out[18]')
print(myprofile.shape)
print(pd.DataFrame(sorted(zip(tfidf_feature_names,
                              user_profiles['.gabriel.'].flatten().tolist()),
                          key=lambda x: -x[1])[:20],
                   columns=['token', 'relevance']))


# In[19]
class ContentBasedRecommender:
    MODEL_NAME = 'Content-Based'

    def __init__(self, items_df=None):
        self.item_ids = item_ids
        self.items_df = items_df

    def get_model_name(self):
        return self.MODEL_NAME

    def _get_similar_items_to_user_profile(self, user, topn=1000):
        cosine_similarities = cosine_similarity(user_profiles[user], tfidf_matrix)
        similar_indices = cosine_similarities.argsort().flatten()[-topn:]
        similar_items = sorted([(item_ids[i], cosine_similarities[0, i]) for i in similar_indices], key=lambda x: -x[1])
        return similar_items

    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        similar_items = self._get_similar_items_to_user_profile(user_id)
        # Ignores items the user has already interacted
        similar_items_filtered = list(filter(lambda x: x[0] not in items_to_ignore, similar_items))

        recommendations_df = pd.DataFrame(similar_items_filtered, columns=['widget', 'rating']) \
            .head(topn)

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how='left',
                                                          left_on='widget',
                                                          right_on='widget')[['widget', 'tag']]

        return recommendations_df


content_based_recommender_model = ContentBasedRecommender(articles_df)

# In[20]
print('')
print('Out[20]')
print('Evaluating Content-Based Filtering model...')
cb_global_metrics, cb_detailed_results_df = model_evaluator.evaluate_model(content_based_recommender_model)
print('\nGlobal metrics:\n%s' % cb_global_metrics)
print('')
print(cb_detailed_results_df.head(10))
