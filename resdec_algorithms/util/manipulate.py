# coding=utf-8
import pandas as pd


# Reduce the dimension of data files.
def reduce_data_dimension(file_ratings=None, file_ratings_sep='|', file_features=None, file_features_sep='|',
                          number_items=10, number_users=10, new_file_rating_path=None, new_file_features_path=None):
    # Data frame for ratings file
    df_ratings = pd.read_csv(file_ratings,
                             encoding='latin-1',
                             sep=file_ratings_sep,
                             # engine='python',
                             header=None,
                             names=['item', 'user', 'rating'])

    # Data frame for features file
    df_features = pd.read_csv(file_features,
                              encoding='latin-1',
                              sep=file_features_sep,
                              names=['plugins', 'tags'])

    # Unique items and only the number of items wanted
    df_unique_items = pd.unique(df_ratings.item.values)[:number_items]
    dic_unique_items = {}
    arr_unique_items = []
    for i in df_unique_items:
        arr_unique_items.append(i)

    dic_unique_items['unique_item'] = arr_unique_items
    df_unique_items = pd.DataFrame(data=dic_unique_items)

    # Merged arrays
    df_merged_items = pd.merge(df_ratings, df_unique_items, left_on='item', right_on='unique_item', how='inner')

    # Group by Item and getting 'n' number of users
    df_group_items = df_merged_items[['item', 'user', 'rating']].groupby('item').head(number_users)
    # Saving the file to csv
    df_group_items.to_csv(new_file_rating_path, index=False, sep='|', header=None, encoding='latin-1')

    # Merged arrays features vs unique items
    df_merged_features = pd.merge(df_features, df_unique_items, left_on='plugins', right_on='unique_item', how='inner')

    # Group by item
    df_group_items_features = df_merged_features[['plugins', 'tags']]
    # Saving the file to csv
    df_group_items_features.to_csv(new_file_features_path, index=False, sep='|', encoding='latin-1')
