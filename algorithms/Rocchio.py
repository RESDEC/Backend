# coding=utf-8
from __future__ import print_function
import pandas as pd

from src.science_concierge.science_concierge import ScienceConcierge
from src.config import configuration
from src.servicios import util

'''Formateo del CSV que se recibe por el necesario para el uso de Rocchio'''
file_path = configuration.FILE_PATH_WORDPRESS_CONTENT  # CSV de WordPress
file_path_new = configuration.file_path_formatted("rocchio")  # CSV formateado
filtro_tag = ['facebook', 'cookie', 'widgets', 'photo', 'youtube']  # Tags filtro que se desee aplicar
sep = '|'
util.convertir_csv_widgets(file_path, file_path_new, filtros_tag=filtro_tag, sep=sep)

'''Primer filtro que buscará la tag deseado en la data de wordpress,
procedimiento que transformara la data de wordpress'''
print('Rocchio >> Leyendo el archivo ' + file_path_new)
df = pd.read_csv(file_path_new, encoding='utf-8')
docs = list(df.tags)
titles = list(df.widgets)

'''Parámetros necesarios para el ScienceConcierge'''
# select weighting from 'count', 'tfidf', or 'entropy'
recommend_model = ScienceConcierge(stemming=True, ngram_range=(1, 1),
                                   weighting='entropy',
                                   norm=None,
                                   n_components=1, n_recommend=30,
                                   verbose=True)

'''Parámetros necesarios para Rocchio'''
recommend_model.fit(docs)  # input list of documents
index = recommend_model.recommend(likes=[10],
                                  dislikes=[])  # input list of like/dislike index (here we like title[10000])
docs_recommend = [titles[i] for i in index[0:5]]  # index[0:5] siendo 5 los widgets a recomendar .

print("Rocchio >> Documentos recomendados a partir de las especificaciones de Rocchio:\n")
for d in docs_recommend:
    print("Rocchio >> - " + d)
