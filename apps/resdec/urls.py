from django.conf.urls import url, include

from . import views

app_name = 'resdec'

urlpatterns = [
    url(r'^list_variability_environments/$', views.list_variability_environment, name='list_variability_environment'),
    url(r'^list_interests/$', views.list_interests, name='list_interests'),
    url(r'^list_features/$', views.list_features, name='list_features'),
    url(r'^cold_start_all/$', views.cold_start_all, name='cold_start_all'),
    url(r'^cold_start_interest/$', views.cold_start_interest, name='cold_start_interest'),
    url(r'^cold_start_features/$', views.cold_start_features, name='cold_start_features'),

    url(r'^list_last_items_used/$', views.list_last_items_used, name='list_last_items_used'),

    url(r'^algorithms/(?P<relation_type>[0-9]+)/$', views.using_algorithms, name='algorithms'),
    url(r'^cold_start/$', views.cold_start_form, name='cold_start_form'),
    url(r'^list_relationship_type_algorithms', views.relationship_type_algorithms, name='relationshipTypeAlgorithms'),
    url(r'^calling_algorithm', views.calling_algorithm, name='calling_algorithm'),
    url(r'^cold_start_calculate', views.cold_start_calculate, name='cold_start_calculate'),
    url(r'^list_variability_environment_items', views.variability_environment_items,
        name='variability_environment_items'),
]
