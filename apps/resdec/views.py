from django.conf import settings
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import RelationshipType, VariabilityEnvironment, VariabilityEnvironmentData, Algorithm, \
    Interest, InterestItemsNames, HistoryUserItems, UserProfile

from resdec_algorithms.cold_start import ColdStart
from resdec_algorithms.based_ratings import TransitionComponentsBasedFeatures as tcbr
from resdec_algorithms.based_features import TransitionComponentsBasedFeatures as tcbf

import json
import pandas as pd
import numpy as np


"""General Functions to the frontend or backend"""


# Login function
def login_view(request):
    username = request.GET.get('username', '')
    password = request.GET.get('password', '')

    user = authenticate(username=username, password=password)

    login = False
    error = 1
    err_msg = 'Incorrect username or password.'
    if user is not None:
        login = True
        error = 0
        err_msg = ''

    data = {
        'error': error,
        'err_msg': err_msg,
        "login": login
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


# Logout function
def logout_view(request):
    logout(request)
    data = {
        'error': 0,
        'err_msg': '',
        'logout': True
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


# Function to get the user data
def user_get(request):
    username = request.GET.get('username', '')
    user = User.objects.get(username__contains=username)
    user_profile = UserProfile.objects.filter(user=user)

    url_photo = ''
    if user_profile:
        url_photo = user_profile[0].avatar.url

    dict_user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'photo': url_photo
    }

    data = {
        'user_data': dict_user_data
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Function to update the user data
def user_put(request):
    username = request.GET.get('username', '')
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    email = request.GET.get('email', '')
    password = request.GET.get('password', '')

    # Getting the user form the data base
    user = User.objects.get(username__contains=username)

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.set_password(password)
    user.save()

    data = {
        'error': 0,
        'err_msg': ''
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Function to update the user photo
def user_photo_upload(request):
    username = request.GET.get('username', '')
    photo = request.FILES['photo']

    user = User.objects.get(username=username)
    user_profile = UserProfile.objects.filter(user=user)

    save_path = 'user_photos/'
    path = default_storage.save(save_path, photo)

    if user_profile:
        user_profile[0].avatar = path
    else:
        UserProfile.objects.create(user=user, avatar=path)

    data = {
        'error': 0,
        'err_msg': ''
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


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
    feature = request.GET.get('feature', '')

    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)

    # Get data file
    variability_environment_data = get_variability_environment_data(
        variability_environment=variability_environment,
        base_on="F")

    error = ''
    dict_features = {}
    if str(variability_environment_data.file) != '':
        print("List Features >> Variability Environment Data: " + str(variability_environment_data.file))
        # DataFrame from reading the csv
        df = pd.read_csv('media/' + str(variability_environment_data.file),
                         encoding='latin-1',
                         sep=str(variability_environment_data.separator))
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


# Function to get the features of an item.
def list_features_item(request):
    variability_environment_id = request.GET.get('var_environment_id', '')
    item = request.GET.get('item', '')

    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)

    # Get data file
    variability_environment_data = get_variability_environment_data(
        variability_environment=variability_environment,
        base_on="F")

    error = 0
    err_msg = ''
    dict_features = {}
    if str(variability_environment_data.file) != '':
        print("List features of item>> Variability Environment Data: " + str(variability_environment_data.file))

        # DataFrame from reading the csv
        df = pd.read_csv('media/' + str(variability_environment_data.file),
                         encoding='latin-1',
                         sep=str(variability_environment_data.separator),
                         names=['plugins', 'tags'])

        # Getting the tags of the item
        x = 9
        for f in df.loc[df['plugins'] == item].tags.values:
            x += 1
            dict_features[x] = f

        if len(dict_features) == 0:
            error = 1
            err_msg = 'No features found for the item: ' + item
    else:
        error = 3
        err_msg = 'No file found to read !!'

    # Loading data response
    data = {
        'error': error,
        'err_msg': err_msg,
        'list_features_item': dict_features
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Getting the last 'n' of items used.
def list_last_items_used(request):
    username = request.GET.get('username', '')
    variability_environment_id = request.GET.get('var_environment_id', '')
    number_items = request.GET.get('number_items', 0)

    try:
        user = User.objects.get(username__contains=username)
    except:
        user = None

    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)

    dict_history_user_items = {}
    if user is not None:
        # Loading a ver with a list of history of items used by the user and filtering a number of them.
        history_user_items = HistoryUserItems.objects.filter(
            user=user,
            variability_environment=variability_environment,
        ).order_by('-date_use')

        # Distinct the items
        arr_item = []
        for hui in history_user_items:
            if hui.item_name not in arr_item:
                arr_item.append(hui.item_name)

        # Items to respond
        x = 0
        for h in arr_item[:int(number_items)]:
            x += 1
            dict_history_user_items[x] = h

        data = {
            'error': 0,
            'err_msg': '',
            'list_last_items_used': dict_history_user_items
        }
    else:
        data = {
            'error': 1,
            'err_msg': "Invalid user",
            'list_last_items_used': dict_history_user_items
        }

    return HttpResponse(json.dumps(data), content_type='application/json')


# List of the items with a specific variability environment and relationship type
def list_items(request):
    variability_environment_id = request.GET.get('var_environment_id', '')
    item = request.GET.get('item', '')

    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)

    # Get data file
    variability_environment_data = get_variability_environment_data(
        variability_environment=variability_environment,
        base_on='R')

    error = 0
    err_msg = ''
    dict_items = {}
    if str(variability_environment_data.file) != '':
        print("List Items >> Variability Environment Data: " + str(variability_environment_data.file))
        # DataFrame from reading the csv
        df = pd.read_csv('media/' + str(variability_environment_data.file),
                         encoding='latin-1',
                         sep=str(variability_environment_data.separator))
        # Items distinct
        items = df[df.columns[0]].unique()
        # Adding features to the dictionary
        x = 0
        for i in items:
            # Check if the input feature, is inside the iterated feature.
            if item in i:
                x += 1
                dict_items[x] = i
    else:
        err_msg = "ERROR: Ups! We don't have a data file with this specifications."

    # Loading data response
    data = {
        'error': error,
        'err_msg': err_msg,
        'list_items': dict_items
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# List of the actives algorithms
def list_algorithms(request):
    relationship_type_id = request.GET.get('relationship_type_id', '')

    relationship_type = get_object_or_404(RelationshipType, pk=relationship_type_id)

    arr_algorithms = Algorithm.objects.filter(
        relationship_type=relationship_type,
        status__contains="A"
    )

    dict_algorithms = {}
    for a in arr_algorithms:
        dict_algorithms[a.pk] = a.name

    data = {
        'list_algorithms': dict_algorithms
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


# Function to get variability environment's data file
def get_variability_environment_data(variability_environment=None, base_on=None):
    variability_environment_data_list = VariabilityEnvironmentData.objects.filter(
        variability_environment=variability_environment,
        base_on__contains=base_on,
        status__contains="A").order_by('-pub_date')

    return variability_environment_data_list[0]


# Function to save the item searched
def save_historic_user_item(user=None, variability_environment=None, item_name=None):
    history = HistoryUserItems(user=user, variability_environment=variability_environment,
                               item_name=item_name)
    history.save()


"""Functions to use Relationship type: Cold Start"""


# Function to calculate the first Cold Start's stage
def cold_start_all(request):
    relationship_type_id = request.GET.get('relationship_type_id', '')
    variability_environment_id = request.GET.get('var_environment_id', '')
    number_recommendations = request.GET.get('number_recommendations', 0)

    relationship_type = get_object_or_404(RelationshipType, pk=relationship_type_id)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)

    variability_environment_data = get_variability_environment_data(
        variability_environment=variability_environment,
        base_on='R')

    print("\nCold Start All >> Relationship Type: " + relationship_type.name)
    print("Cold Start All >> Variability Environment: " + variability_environment.name)

    cold_start_recommendations = {}
    possible_interest_recommendations = {}
    if str(variability_environment_data.name) != '':
        # DataFrame from reading the csv
        df = pd.read_csv('media/' + str(variability_environment_data.file),
                         encoding='latin-1',
                         sep=str(variability_environment_data.separator))
        # Distinct items in the cvs
        items = df[df.columns[0]].unique()

        # Adding items to the dictionary
        dict_items = {}
        x = 0
        for i in items:
            x += 1
            dict_items[x] = i

        number_recommendations = int(number_recommendations)

        # Calling to the ColdStart class
        cs = ColdStart(file_rating_path='media/' + str(variability_environment_data.file),
                       delimiter=variability_environment_data.separator,
                       dict_items=dict_items,
                       number_recommendations=number_recommendations + 4)
        recommendations = cs.calculate_cold_start()

        for x in list(recommendations)[0:number_recommendations]:
            cold_start_recommendations[x] = recommendations[x]

        for x in list(recommendations)[number_recommendations:]:
            possible_interest_recommendations[x] = recommendations[x]

    data = {
        'cold_start_recommendations': cold_start_recommendations,
        'possible_interest_recommendations': possible_interest_recommendations
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
        variability_environment=variability_environment,
        base_on='R')

    print("\nCold Start Interest >> Relationship Type: " + relationship_type.name)
    print("Cold Start Interest >> Variability Environment: " + variability_environment.name)
    print("Cold Start Interest >> Interest: " + interest.name)

    cold_start_recommendations = {}
    possible_interest_recommendations = {}
    if str(variability_environment_data.name) != '':
        # Loading interest's items to a dictionary
        dict_items = {}
        x = 0
        for i in interest_items:
            x += 1
            dict_items[x] = i.item_name.strip()

        number_recommendations = int(number_recommendations)

        # Calling to the ColdStart class
        cs = ColdStart(file_rating_path='media/' + str(variability_environment_data.file),
                       delimiter=variability_environment_data.separator,
                       dict_items=dict_items,
                       number_recommendations=number_recommendations + 4)
        recommendations = cs.calculate_cold_start()

        for x in list(recommendations)[0:number_recommendations]:
            cold_start_recommendations[x] = recommendations[x]

        for x in list(recommendations)[number_recommendations:]:
            possible_interest_recommendations[x] = recommendations[x]

    data = {
        'cold_start_recommendations': cold_start_recommendations,
        'possible_interest_recommendations': possible_interest_recommendations
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
        variability_environment=variability_environment,
        base_on="F"
    )

    print("\nCold Start Features >> Relationship Type: " + relationship_type.name)
    print("Cold Start Features >> Variability Environment: " + variability_environment.name)
    print("Cold Start Features >> Features selected: " + str(len(arr_features_filter)))

    print("Cold Start Features >> Variability Environment Data Features: " +
          str(variability_environment_data_features.file))

    # Getting data file with the features.
    arr_data_fea_csv = np.genfromtxt('media/' + str(variability_environment_data_features.file),
                                     delimiter=str(variability_environment_data_features.separator),
                                     dtype=None)

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
        variability_environment=variability_environment,
        base_on='R')

    cold_start_recommendations = {}
    possible_interest_recommendations = {}
    number_recommendations = int(number_recommendations)

    # Calling to the ColdStart class
    cs = ColdStart(file_rating_path='media/' + str(variability_environment_data_rating.file),
                   delimiter=variability_environment_data_rating.separator,
                   dict_items=dict_items,
                   number_recommendations=number_recommendations + 4)
    recommendations = cs.calculate_cold_start()

    for x in list(recommendations)[0:number_recommendations]:
        cold_start_recommendations[x] = recommendations[x]

    for x in list(recommendations)[number_recommendations:]:
        possible_interest_recommendations[x] = recommendations[x]

    data = {
        'cold_start_recommendations': cold_start_recommendations,
        'possible_interest_recommendations': possible_interest_recommendations
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


"""Functions to use Relationship type: Transition of components based on ratings"""


def transition_components_based_ratings(request):
    relationship_type_id = request.GET.get('relationship_type_id', '')
    variability_environment_id = request.GET.get('var_environment_id', '')
    algorithm_id = request.GET.get('algorithm_id', '')
    item_evaluated = request.GET.get('item_evaluated', '')
    number_recommendations = request.GET.get('number_recommendations', '')
    username = request.GET.get('username', '')

    relationship_type = get_object_or_404(RelationshipType, pk=relationship_type_id)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)
    algorithm = get_object_or_404(Algorithm, pk=algorithm_id)
    user = User.objects.get(username__contains=username)

    variability_environment_data = get_variability_environment_data(
        variability_environment=variability_environment,
        base_on='R')

    print("\nTransition Component Based Rating >> Relationship Type: " + relationship_type.name)
    print("Transition Component Based Rating >> Variability Environment: " + variability_environment.name)
    print("Transition Component Based Rating >> Item to evaluated: " + item_evaluated)
    print("Transition Component Based Rating >> Algorithm: " + algorithm.name)

    number_recommendations = int(number_recommendations)

    tran_comp_rating_recommendation = {}
    possible_interest_recommendations = {}
    recommendations = {}

    if str(variability_environment_data.name) != '':
        if algorithm.pk == 11:
            recommendations = \
                tcbr(file_path='media/' + str(variability_environment_data.file),
                     delimiter=variability_environment_data.separator,
                     item_evaluated=item_evaluated,
                     number_recommendations=number_recommendations + 4).svd()
        elif algorithm.pk == 13:
            recommendations = \
                tcbr(file_path='media/' + str(variability_environment_data.file),
                     delimiter=variability_environment_data.separator,
                     item_evaluated=item_evaluated,
                     number_recommendations=number_recommendations + 4).knn_basic()
        elif algorithm.pk == 14:
            recommendations = \
                tcbr(file_path='media/' + str(variability_environment_data.file),
                     delimiter=variability_environment_data.separator,
                     item_evaluated=item_evaluated,
                     number_recommendations=number_recommendations + 4).knn_centered()

        else:
            pass

    # Saving item used
    save_historic_user_item(user=user, variability_environment=variability_environment, item_name=item_evaluated)

    for x in list(recommendations)[0:number_recommendations]:
        tran_comp_rating_recommendation[x] = recommendations[x]

    for x in list(recommendations)[number_recommendations:]:
        possible_interest_recommendations[x] = recommendations[x]

    data = {
        'tran_comp_rating_recommendation': tran_comp_rating_recommendation,
        'possible_interest_recommendations': possible_interest_recommendations
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


"""Functions to use Relationship type: Transition of components based on content"""


def transition_components_based_features(request):
    relationship_type_id = request.GET.get('relationship_type_id', '')
    variability_environment_id = request.GET.get('var_environment_id', '')
    algorithm_id = request.GET.get('algorithm_id', '')
    item_evaluated = request.GET.get('item_evaluated', '')
    number_recommendations = request.GET.get('number_recommendations', '')
    username = request.GET.get('username', '')

    relationship_type = get_object_or_404(RelationshipType, pk=relationship_type_id)
    variability_environment = get_object_or_404(VariabilityEnvironment, pk=variability_environment_id)
    algorithm = get_object_or_404(Algorithm, pk=algorithm_id)
    user = User.objects.get(username__contains=username)

    variability_environment_data = get_variability_environment_data(
        variability_environment=variability_environment,
        base_on='F')

    print("\nTransition Component Based Features >> Relationship Type: " + relationship_type.name)
    print("Transition Component Based Features >> Variability Environment: " + variability_environment.name)
    print("Transition Component Based Features >> Item to evaluated: " + item_evaluated)
    print("Transition Component Based Features >> Algorithm: " + algorithm.name)

    number_recommendations = int(number_recommendations)

    tran_comp_featuring_recommendation = {}
    possible_interest_recommendations = {}
    recommendations = {}

    if str(variability_environment_data.name) != '':
        # Calling the algorithm
        if algorithm.pk == 16:
            tran_comp_bas_fea = tcbf(file_path='media/' + str(variability_environment_data.file),
                                     delimiter=variability_environment_data.separator,
                                     item_evaluated=item_evaluated,
                                     number_recommendations=number_recommendations + 4)

            recommendations = tran_comp_bas_fea.tf_idf_cosine_similarity(
                item_col=variability_environment_data.item_column,
                features_col=variability_environment_data.feature_column)

        else:
            pass

    # Saving item used
    save_historic_user_item(user=user, variability_environment=variability_environment, item_name=item_evaluated)

    for x in list(recommendations)[0:number_recommendations]:
        tran_comp_featuring_recommendation[x] = recommendations[x]

    for x in list(recommendations)[number_recommendations:]:
        possible_interest_recommendations[x] = recommendations[x]

    data = {
        'tran_comp_featuring_recommendation': tran_comp_featuring_recommendation,
        'possible_interest_recommendations': possible_interest_recommendations
    }

    return HttpResponse(json.dumps(data), content_type='application/json')
