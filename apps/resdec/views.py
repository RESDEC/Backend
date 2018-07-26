from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core import serializers

from algorithms import CollaborativeFilterAlgorithmsFun, SVD
from .models import RelationshipType, VariabilityEnvironment, VariabilityEnvironmentData, Algorithm, \
    Interest, InterestItemsNames

import json
import random
import pandas as pd
import numpy as np


def using_algorithms(request, relation_type=None):
    # Getting relationship type with the pk
    rel_type = get_object_or_404(RelationshipType, pk=relation_type)
    # Getting variability environments
    var_environments = VariabilityEnvironment.objects.all()
    # Getting data files
    var_env_data = VariabilityEnvironmentData.objects.all()
    # return render
    return render(request, 'resdec/algorithms.html', {'rel_type': rel_type,
                                                      'var_environments': var_environments,
                                                      'var_env_data': var_env_data,
                                                      })


@login_required
def cold_start_form(request):
    # Getting relationship type Cold Start
    rel_type = get_object_or_404(RelationshipType, pk=1)
    # Getting variability environments
    var_environments = VariabilityEnvironment.objects.all()
    # return render
    return render(request, 'resdec/cold_start.html', {'rel_type': rel_type,
                                                      'var_environments': var_environments,
                                                      })


# Return all the algorithms with the relationship type in the request.
def relationship_type_algorithms(request):
    rt_pk = request.GET.get('relationType', '')  # dictionary (request.GET)
    relationship_type = get_object_or_404(RelationshipType, pk=rt_pk)

    print("Relationship Type: " + str(relationship_type.name))

    algorithms_serializers = serializers.serialize('json',
                                                   Algorithm.objects.filter(relationship_type__exact=relationship_type,
                                                                            status='A', ))

    return HttpResponse(json.dumps(algorithms_serializers), content_type="application/json")


def variability_environment_items(request):
    # Loading variables with the data from the request
    pk_relationship_type = request.GET.get('relationshipType')
    pk_variability_environment = request.GET.get('variabilityEnvironment')

    # Loading models from the primary keys
    relationship_type = get_object_or_404(RelationshipType, pk=pk_relationship_type)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=pk_variability_environment)
    variability_environment_data_list = VariabilityEnvironmentData.objects.filter(
        relationship_type=relationship_type,
        variability_environment=variability_environment,
        status="A").order_by('-pub_date')

    # Variables to response
    dict_features = {}
    error = ''

    # Getting csv file of the last variability environment and relationship type
    if variability_environment_data_list.count() != 0:
        # Loading variable with data of variability environment
        variability_environment_data = variability_environment_data_list[0]
        print("Variability Environment Data: " + str(variability_environment_data.file))

        # DataFrame from reading the csv
        df = pd.read_csv(str(variability_environment_data.file), encoding='latin-1', sep="|")

        # Distinct items in the cvs
        items = df[df.columns[0]].unique()

        # Adding items to the dictionary
        dict_features = {}
        x = 0
        for i in items:
            x += 1
            dict_features[x] = i
    else:
        error = "Ups! We don't have a data file for this variability environment"

    # csv_path = BASE_DIR + "\\static\\data\\generated\\" + variability_environment_data

    # Loading backend response
    data = {'error': error,
            'dict_items': dict_features
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


def data_serializer(data):
    return {'id': data.id, 'name': data.name}


# Deprecated
def calling_algorithm(request):
    # Loading the variables from the GET request
    algorithm_rel_type = request.GET.get('algorithm_rel_typ', '')
    algorithm_var_env = request.GET.get('algorithm_var_env', '')
    algorithm_data = request.GET.get('algorithm_data', '')
    algorithm_id = request.GET.get('algorithm_id', '')
    algorithm_str = request.GET.get('algorithm_str', '')

    # Loading variables with the models.
    relationship_type = get_object_or_404(RelationshipType, pk=int(algorithm_rel_type))
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=int(algorithm_var_env))

    # Messages
    print("Using Variavility Environment: " + algorithm_var_env)
    print("Using Data: " + algorithm_data)
    print("Using Algorithm: " + algorithm_id)

    # Check what is the algorithm to use.

    # SVD.svd(file_path=BASE_DIR + "\\static\\data\\generated\\ratings_corregido.csv", sep="|")

    dict_result = {"google": random.uniform(0, 1),
                   "facebook": random.uniform(0, 1),
                   "youtube": random.uniform(0, 1),
                   }

    data = [
        ('html_response_table', create_table_html(variability_env=variability_environment.name, dict_data=dict_result,
                                                  str_algorithm=algorithm_str)), ]

    return HttpResponse(json.dumps(dict(data)),
                        content_type='application/json'
                        )


# Function to calculate cold start's algorithms
def cold_start_calculate(request):
    # Loading variables from the GET request
    pk_relationship_type = request.GET.get('relationshipType')
    pk_variability_environment = int(request.GET.get('algorithm_var_env', ''))
    pk_algorithm = int(request.GET.get('algorithm_id', ''))
    number_recommendations = int(request.GET.get('number_recommendations', ''))
    # arr_selected_items = request.GET.get('selected_items', '')
    arr_selected_items = request.GET.getlist('selected_items[]')

    # Loading models from the primary keys
    relationship_type = get_object_or_404(RelationshipType, pk=pk_relationship_type)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=pk_variability_environment)
    algorithm = get_object_or_404(Algorithm, pk=pk_algorithm)
    variability_environment_data_list = VariabilityEnvironmentData.objects.filter(
        relationship_type=relationship_type,
        variability_environment=variability_environment,
        status="A").order_by('-pub_date')

    # Messages
    print("Using variability environment: " + variability_environment.name)
    print("Using algorithm: " + algorithm.name)
    print("Number of recommendations: " + str(number_recommendations))
    print("Items to filter: ")
    for i in arr_selected_items:
        print("- " + str(i))

    # Loading the filters
    arr_items_filter = np.array(arr_selected_items)
    dict_result_all = {}
    dict_result = {}

    # Reading csv data file
    if variability_environment_data_list.count() != 0:
        # Loading variable with data of variability environment
        variability_environment_data = variability_environment_data_list[0]
        print("Variability Environment Data: " + str(variability_environment_data.file))

        arr_data_csv = np.genfromtxt(str(variability_environment_data.file), delimiter='|', dtype=None)

        list_result = []
        for itm in arr_items_filter:
            itm_count = 0
            itm_sum = 0
            itm_avg = 0.0

            for data in arr_data_csv:
                if str(itm).strip() == str(data[0]).strip():
                    itm_count += 1
                    itm_sum += data[2]

            if itm_count > 0:
                itm_avg = itm_sum / float(itm_count)

            print("For itm: " + itm + " Sum: " + str(itm_sum) + " Count: " + str(itm_count) +
                  " Avg:" + str(itm_avg))

            tuple_result = (itm, itm_avg)
            list_result.append(tuple_result)

        # Sort list of tuples
        sorted(list_result, key=lambda x: x[1])

        # List of tuples to dictionary
        dict_result_all = dict(list_result)

    if dict_result_all.__len__() > 0:
        row = 0
        for key, value in dict_result_all.iteritems():
            row += 1
            dict_result[key] = value
            if row >= number_recommendations:
                break

    data = [
        ('html_response_table', create_table_html(variability_env=variability_environment.name, dict_data=dict_result,
                                                  str_algorithm=algorithm.name)), ]

    return HttpResponse(json.dumps(dict(data)), content_type='application/json')


def create_table_html(variability_env=None, dict_data=None, str_algorithm=None):
    # Creating the table header
    html_table = '<table id="datatable" class="striped">' \
                 '<thead>' \
                 '<tr>' \
                 '<th></th>' \
                 '<th style="text-align: center;">' + \
                 str_algorithm + \
                 '</th>' \
                 '</thead>' \
                 '<tbody>'

    # Reading dictionary to complete the table's body
    for x in dict_data:
        html_table += '<tr><td>' + x + '</td><td style="text-align: center;">' + str(dict_data[x]) + '</td></tr>'
    html_table += '</tbody></table>'
    return html_table


# Function to get variability environment's data file
def get_variability_environment_data(variability_environment=None, relationship_type=None, base_on=None):
    variability_environment_data_list = VariabilityEnvironmentData.objects.filter(
        variability_environment=variability_environment,
        relationship_type=relationship_type,
        base_on__contains=base_on,
        status__contains="A").order_by('-pub_date')

    return variability_environment_data_list[0]


# Function to work with relationship type Cold Start. It only need some parameters to calculate in its all scenarios.
def get_calculate_cold_start(dict_items=None, variability_environment_data=None, number_recommendations=None):
    print("Calculating Cold Start >> Items to Evaluate: " + str(dict_items.__len__()))
    print("Calculating Cold Start >> Variability Environment Data: " + variability_environment_data.name)
    print("Calculating Cold Start >> Number of recommendations: " + str(number_recommendations))

    # DataFrame from reading the csv
    arr_data_csv = np.genfromtxt(str(variability_environment_data.file), delimiter='|', dtype=None)
    # Dictionary with items and values
    dict_items_values = {}
    for key, value in dict_items.iteritems():
        # Dictionary of items, to store counter and sum
        dict_items_values[value] = [0, 0.00]

    # Iterating csv file
    for data in arr_data_csv:
        if str(data[0]).strip() in dict_items_values.keys():
            # Storing the counter
            dict_items_values[str(data[0]).strip()][0] += 1
            # Storing the value
            dict_items_values[str(data[0]).strip()][1] += data[2]

    list_result = []
    for key, value in dict_items_values.iteritems():
        if value[0] > 0:
            tuple_result = (key, value[1]/value[0])
            list_result.append(tuple_result)

    # Sort list of tuples
    sorted(list_result, key=lambda x: x[1])

    # List of tuples to dictionary
    dict_items_all = dict(list_result)

    # Limiting number of recommendations
    dict_items_result = {}
    if dict_items_all.__len__() > 0:
        row = 0
        for key, value in dict_items_all.iteritems():
            row += 1
            dict_items_result[key] = value
            if row >= int(number_recommendations):
                break

    return dict_items_result


# This function respond a collection with the variability environments
def list_variability_environment(request):
    variability_environment_list = VariabilityEnvironment.objects.filter(status__contains='A')
    variability_environments = {}
    for ve in variability_environment_list:
        variability_environments[ve.pk] = ve.name

    data = {
        'variability_environments': variability_environments
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


# Function what respond a collection with the actives interests in the system
def list_interests(request):
    variability_environment_id = request.GET.get('var_environment_id', 0)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)
    # Interest with the variability environment defined from frontend
    interests = Interest.objects.filter(variability_environment=variability_environment,
                                        status__contains='A')

    interests_list = {}
    for i in interests:
        interests_list[i.pk] = i.name

    data = {
        'list_interests': interests_list
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Function what respond a collection with the features in the data file.
def list_features(request):
    variability_environment_id = request.GET.get('var_environment_id', 0)
    relationship_type_id = request.GET.get('relationship_type_id', 0)
    feature = request.GET.get('feature', '')

    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)
    relationship_type = get_object_or_404(RelationshipType, pk=relationship_type_id)

    # Get data file
    variability_environment_data = get_variability_environment_data(
        variability_environment=variability_environment,
        relationship_type=relationship_type,
        base_on="F")

    error = ''
    dict_features = {}
    if str(variability_environment_data.file) != '':
        print("List Features >> Variability Environment Data: " + str(variability_environment_data.file))
        # DataFrame from reading the csv
        df = pd.read_csv(str(variability_environment_data.file), encoding='latin-1', sep="|")
        # Features distinct.
        features = df[df.columns[1]].unique()
        # Adding features to the dictionary
        x = 0
        for f in features:
            # Check if the input feature, is inside the iterated feature.
            if feature in f:
                x += 1
                dict_features[x] = f
    else:
        error = "ERROR: Ups! We don't have a data file with this specifications."

    # Loading data response
    data = {
        'error': error,
        'list_features': dict_features
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Function to calculate the first Cold Start's stage
def cold_start_all(request):
    relationship_type_id = request.GET.get('relationship_type_id', '')
    variability_environment_id = request.GET.get('var_environment_id', '')
    number_recommendations = request.GET.get('number_recommendations', 0)

    relationship_type = get_object_or_404(RelationshipType, pk=relationship_type_id)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)

    variability_environment_data = get_variability_environment_data(
        relationship_type=relationship_type,
        variability_environment=variability_environment,
        base_on='R')

    cold_start_recommendations = {}
    if str(variability_environment_data.name) != '':
        print("Cold Start All >> Variability Environment Data: " + str(variability_environment_data.file))

        # DataFrame from reading the csv
        df = pd.read_csv(str(variability_environment_data.file), encoding='latin-1', sep="|")
        # Distinct items in the cvs
        items = df[df.columns[0]].unique()

        # Adding items to the dictionary
        dict_items = {}
        x = 0
        for i in items:
            x += 1
            dict_items[x] = i

        cold_start_recommendations = get_calculate_cold_start(
            dict_items=dict_items,
            variability_environment_data=variability_environment_data,
            number_recommendations=number_recommendations
        )

    data = {
        'cold_start_recommendations': cold_start_recommendations
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Function to calculate the second Cold Start's stage
def cold_start_interest(request):
    relationship_type_id = request.GET.get('relationship_type_id', '')
    variability_environment_id = request.GET.get('var_environment_id', '')
    interest_id = request.GET.get('interest_id', 0)
    number_recommendations = request.GET.get('number_recommendations', '')

    relationship_type = get_object_or_404(RelationshipType, pk=int(relationship_type_id))
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=int(variability_environment_id))
    interest = get_object_or_404(Interest, pk=int(interest_id))
    interest_items = InterestItemsNames.objects.filter(interest=interest)

    variability_environment_data = get_variability_environment_data(
        relationship_type=relationship_type,
        variability_environment=variability_environment,
        base_on='R')

    cold_start_recommendations = {}
    if str(variability_environment_data.name) != '':
        print("Cold Start Interest >> Variability Environment Data: " + str(variability_environment_data.file))

        # Loading interest's items to a dictionary
        dict_items = {}
        x = 0
        for i in interest_items:
            x += 1
            dict_items[x] = i.item_name.strip()

        # Call the function that resolve the cold start relationship type
        cold_start_recommendations = get_calculate_cold_start(
            dict_items=dict_items,
            variability_environment_data=variability_environment_data,
            number_recommendations=number_recommendations
        )

    data = {
        'cold_start_recommendations': cold_start_recommendations
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Function to calculate the third Cold Start's stage
def cold_start_features(request):
    relationship_type_id = request.GET.get('relationship_type_id', '')
    variability_environment_id = request.GET.get('var_environment_id', '')
    arr_features_filter = request.GET.getlist('selected_features[]')
    number_recommendations = request.GET.get('number_recommendations', '')

    relationship_type = get_object_or_404(RelationshipType, pk=relationship_type_id)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)

    # Loading csv file with the features for this relationship type and environment
    variability_environment_data_features = get_variability_environment_data(
        relationship_type=relationship_type,
        variability_environment=variability_environment,
        base_on="F"
    )

    print("Cold Start Features >> Variability Environment Data Features: " +
          str(variability_environment_data_features.file))

    # Getting data file with the features.
    arr_data_fea_csv = np.genfromtxt(str(variability_environment_data_features.file), delimiter='|', dtype=None)

    # Encoding features
    arr_features = []
    for f in arr_features_filter:
        arr_features.append(f.encode('utf-8'))

    # Getting items what have the features filtered
    dict_items = {}
    x = 0
    for data in arr_data_fea_csv:
        if data[1].strip() in arr_features:
            x += 1
            dict_items[x] = data[0]

    # Getting the rating data to calculate cold start with the items filtered.
    variability_environment_data_rating = get_variability_environment_data(
        relationship_type=relationship_type,
        variability_environment=variability_environment,
        base_on='R')

    # Call the function that resolve the cold start relationship type
    cold_start_recommendations = get_calculate_cold_start(
        dict_items=dict_items,
        variability_environment_data=variability_environment_data_rating,
        number_recommendations=number_recommendations
    )

    data = {
        'cold_start_recommendations': cold_start_recommendations
    }

    return HttpResponse(json.dumps(data), content_type='application/json')
