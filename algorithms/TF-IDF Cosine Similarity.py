# coding=utf-8
from __future__ import print_function
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from src.config import configuration
from src.servicios import util


def find_similar(tfidf_matrix, index, top_n=2):
    cosine_similarities = linear_kernel(tfidf_matrix[index:index + 1], tfidf_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != index]
    return [(index, cosine_similarities[index]) for index in related_docs_indices][0:top_n]


'''Formateo del CSV que se recibe por el necesario para el uso de TF-IDF'''
file_path = configuration.FILE_PATH_WORDPRESS_CONTENT  # CSV de WordPress
file_path_new = configuration.file_path_formatted("tf-idf")  # CSV formateado
filtros_tag = []  # Tags filtro que se desee aplicar
sep = '|'
util.convertir_csv_widgets(file_path, file_path_new, filtros_tag, sep=sep)

'''Leyendo CSV de WordPress formateado y preparando parámetros para usar TF-IDF'''
corpus = []  # Matrix to get all the values from the CSV
# Getting cols what I need form the CSV
print('TF- IDF >> Leyendo el archivo ' + file_path_new)
df = pd.read_csv(file_path_new, encoding='utf-8')  # Leyendo csv de wordpress formateado
docs = list(df.tags)  # lista de tags
titles = list(df.widgets)  # lista de widgets
var = df.values  # CSV -> Array

i = 0
while i < titles.__len__():
    if titles[i] and docs[i]:
        corpus.append((titles[i], docs[i]))
        # corpus.append((docs[i], titles[i]))
        widget = docs[i]
        title = titles[i]
        # print ("- ", doc)
        i += 1

'''Usando TF-IDF'''
tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform([content for file, content in corpus])
widget = 13  # Widget a comparar

print("\nTF- IDF >> Documentos recomendados con TIF-IDF y Coseno de Similitud a partir del widget:")
print("TF- IDF >> '", corpus[widget][0], "'\n")
for index, score in find_similar(tfidf_matrix, widget):
    print("TF- IDF >> - ", score, corpus[index][0])
