from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers

from algorithms import SVD
from .models import RelationshipType, VariabilityEnvironment, VariabilityEnvironmentData

import json


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
    relTypes = RelationshipType.objects.filter(pk=relation_type)
    varEnvironments = VariabilityEnvironment.objects.all()
    varEnvData = VariabilityEnvironmentData.objects.all()
    return render(request, 'resdec/algorithms.html',
                  {'relTypes': relTypes,
                   'varEnvironments': varEnvironments,
                   'varEnvData': varEnvData,
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
    algorith_var_env = request.GET.get('algorith_var_env', '')
    algorithm_data = request.GET.get('algorithm_data', '')
    algorithm_id = request.GET.get('algorithm_id', '')

    print("Using Variavility Environment: " + algorith_var_env)
    print("Using Data: " + algorithm_data)
    print("Using Algorithm: " + algorithm_id)

    return None
