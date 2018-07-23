from django.conf.urls import url, include

from . import views

app_name = 'resdec'

urlpatterns = [
    url(r'^algorithms/(?P<relation_type>[0-9]+)/$', views.using_algorithms, name='algorithms'),
    url(r'^cold_start/$', views.cold_start_form, name='cold_start_form'),
    url(r'^list_relationship_type_algorithms', views.relationship_type_algorithms, name='relationshipTypeAlgorithms'),
    # url(r'^list_variability_environments_data', views.variability_environment_data, name='variabilityEnvironmentData'),
    url(r'^calling_algorithm', views.calling_algorithm, name='calling_algorithm'),
    url(r'^cold_start_calculate', views.cold_start_calculate, name='cold_start_calculate'),
    url(r'^list_variability_environment_items', views.variability_environment_items,
        name='variability_environment_items'),
]
