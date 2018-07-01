from __future__ import print_function
from random import randint
import pandas as pd


def correct_format_csv_features(file_path_in, filtros_tag, sep):
    """Formatea el csv de entrada de modo que todos los features queden concatenados dentro de una sola columna es decir:
    De:
        entity | feature1 | feature2 | feature3... | featureN
    A:
        entity | feature1 feature2 feature3... featureN"""

    file_path_out = file_path_generated(file_path_in)

    if not filtros_tag:
        print('Correct features format CSV >> No filter tags.')
    else:
        print('Correct features format CSV >> Tags filter:')
        for i in filtros_tag:
            print('Correct features format CSV >> - ' + i)

    df = pd.read_csv(file_path_in, encoding='utf-8', sep=sep)
    widgets = list(df.widgets.unique())  # provide list unique of entities
    arr_csv = pd.read_csv(file_path_in, header=None, sep=sep)

    # Compara los widgets unicos contra el array del CSV
    arr = []
    for w in widgets:
        w_tags = ''
        exist_tag = False
        # for wid, tag, val in arr_csv.values:
        for wid, tag in arr_csv.values:
            if wid == w:
                w_tags += tag + ' '
                for f in filtros_tag:
                    if f in tag:
                        exist_tag = True
                        break
        if not filtros_tag:
            arr.append([w_tags, w])
        else:
            if exist_tag:
                arr.append([w_tags, w])

    arr_out = pd.DataFrame(arr)
    arr_out.to_csv(file_path_out, index=False, header=['tags', 'widgets'])


def correct_format_csv_etv(file_path_in, sep=","):
    """Formatea la matriz que ingrese y genera una matriz de forma correcta con la estructura:
    entidad | tag | valoracion """

    file_path_out = file_path_generated(file_path_in)
    print('Correct Format CSV >> Reading file ' + file_path_in)
    arr_csv = []
    i = 0
    for line in open(file_path_in):
        arr = line.split(sep)
        i += 1
        if arr.__len__() == 3:
            arr_new = [arr[0], arr[1], arr[2].replace("\n", "")]
        else:
            print('Correct Format CSV >> A row with errors has be found, correcting. Row: ' + str(i))
            x = 1
            y = arr.__len__() - 1
            tag = ''
            while x < y:
                tag += arr[x]
                x += 1

            arr_new = [arr[0], tag, arr[y].replace("\n", "")]

        arr_csv.append(arr_new)

    arr_out = pd.DataFrame(arr_csv)
    arr_out.to_csv(file_path_out, index=False, header=False, sep=sep)
    print('Correct Format CSV >> The file has been generated: ' + file_path_out)


def file_path_generated(file_path):
    """Devuelve la ruta para el nuevo archivo que se encuentra revisado y formateado"""
    f = open(file_path)
    return "../resources/data/generated/" + f.name + "_formatted_" + str(randint(0, 1000)) + ".csv"
