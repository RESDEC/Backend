from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers

from .models import RelationshipType, VariabilityEnvironment, VariabilityEnvironmentData

import json


COLD_START = [
    ('cst', 'Cold Start'),
]

COLLABORATIVE = [
    ('bso', 'Base Only'),
    ('coc', 'CoClustering'),
    ('kne', 'K-Nearest Neighbors'),
    ('knb', 'KNN BaseLine'),
    ('knc', 'KNN Basic'),
    ('knw', 'KNN With Means'),
    ('nmf', 'NMF'),
    ('nmp', 'Normal Prediction'),
    ('slo', 'Slop One'),
    ('svd', 'SVD'),
    ('svp', 'SVDpp'),
]

CONTENT = [
    ('roc', 'Rocchio'),
    ('tfd', 'TF-IDF Cosine Similarity'),
]


# Create your views here.
def index(request):
    return render(request, 'index.html', )


def algorithms(request):
    relTypes = RelationshipType.objects.all()
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
