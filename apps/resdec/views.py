from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core import serializers

from algorithms import CollaborativeFilterAlgorithmsFun
from .models import RelationshipType, VariabilityEnvironment, VariabilityEnvironmentData

import json
import random

COLD_START = [
    ('cst', 'Cold Start'),
]

COLLABORATIVE = [
    # ('bso', 'Base Only'),
    # ('coc', 'CoClustering'),
    # ('kne', 'K-Nearest Neighbors'),
    # ('knb', 'KNN BaseLine'),
    # ('knc', 'KNN Basic'),
    # ('knw', 'KNN With Means'),
    # ('nmf', 'NMF'),
    # ('nmp', 'Normal Prediction'),
    # ('slo', 'Slop One'),
    ('svd', 'SVD'),
    # ('svp', 'SVDpp'),
    ('utu', 'User to user'),
    ('iti', 'Item to item'),
]

CONTENT = [
    # ('roc', 'Rocchio'),
    ('tfd', 'TF-IDF Cosine Similarity'),
]


# Create your views here.
def index(request):
    return render(request, 'index.html', )


def algorithms(request, relation_type=None):
    rel_type = get_object_or_404(RelationshipType, pk=relation_type)
    var_environments = VariabilityEnvironment.objects.all()
    var_env_data = VariabilityEnvironmentData.objects.all()
    return render(request, 'resdec/algorithms.html',
                  {'rel_type': rel_type,
                   'var_environments': var_environments,
                   'var_env_data': var_env_data,
                   })


def relationship_type_algorithms(request):
    rel = request.GET.get('relationType')  # dictionary (request.GET)
    print("Relationship Type: " + rel)
    if rel == '2':
        return HttpResponse(json.dumps(dict(COLLABORATIVE)), content_type='application/json')
    elif rel == '3':
        return HttpResponse(json.dumps(dict(CONTENT)), content_type='application/json')
    else:
        return HttpResponse(json.dumps(dict(COLD_START)), content_type='application/json')


def variability_environment_data(request):
    env = request.GET.get('variabilityEnvironment')
    print("Variability Environment: " + env)
    varEnvDatas = VariabilityEnvironmentData.objects.filter(variability_environment__id=env)
    varEnvDatas = [data_serializer(data) for data in varEnvDatas]
    return HttpResponse(json.dumps(varEnvDatas), content_type='application/json')


def data_serializer(data):
    return {'id': data.id, 'name': data.name}


def calling_algorithm(request):
    algorithm_rel_type = request.GET.get('algorithm_rel_typ', '')
    algorithm_var_env = request.GET.get('algorithm_var_env', '')
    algorithm_data = request.GET.get('algorithm_data', '')
    algorithm_id = request.GET.get('algorithm_id', '')
    algorithm_str = request.GET.get('algorithm_str', '')

    print("Using Variavility Environment: " + algorithm_var_env)
    print("Using Data: " + algorithm_data)
    print("Using Algorithm: " + algorithm_id)

    str_relation_type = get_object_or_404(RelationshipType, pk=int(algorithm_rel_type)).name
    str_varibility_env = get_object_or_404(VariabilityEnvironment, pk=int(algorithm_var_env)).name

    # message = CollaborativeFilterAlgorithmsFun.start()

    dict_result = {"google": random.uniform(0, 1),
                   "facebook": random.uniform(0, 1),
                   "youtube": random.uniform(0, 1),
                   }

    data = [('html_response_table', create_table_html(variability_env=str_varibility_env, dict_data=dict_result,
                                                      str_algorithm=algorithm_str)), ]

    return HttpResponse(json.dumps(dict(data)),
                        content_type='application/json'
                        )


def create_table_html(variability_env=None, dict_data=None, str_algorithm=None):
    print(dict_data)
    # Cabecera de la tabla.
    html_table = '<table id="datatable" class="striped">' \
                 '<thead>' \
                 '<tr>' \
                 '<th></th>' \
                 '<th style="text-align: center;">' + str_algorithm + '</th>' \
                                                                      '</thead>' \
                                                                      '<tbody>'

    for x in dict_data:
        html_table += '<tr><td>' + x + '</td><td style="text-align: center;">' + str(dict_data[x]) + '</td></tr>'
    html_table += '</tbody></table>'
    return html_table
