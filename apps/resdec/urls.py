from django.conf.urls import url

from . import views


app_name = 'resdec'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^algorithms/(?P<relation_type>[0-9]+)/$', views.algorithms, name='algorithms'),
    url(r'^list_relationship_type_algorithms', views.relationship_type_algorithms, name='relationshipTypeAlgorithms'),
    url(r'^list_variability_environments_data', views.variability_environment_data, name='variabilityEnvironmentData'),
]
