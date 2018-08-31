from django.conf.urls import url, include

from . import views

app_name = 'resdec'

urlpatterns = [
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^list_variability_environments/$', views.list_variability_environment, name='list_variability_environment'),
    url(r'^list_interests/$', views.list_interests, name='list_interests'),
    url(r'^list_features/$', views.list_features, name='list_features'),
    url(r'^list_features_item/$', views.list_features_item, name='list_features_item'),

    url(r'^list_last_items_used/$', views.list_last_items_used, name='list_last_items_used'),
    url(r'^list_items/$', views.list_items, name='list_items'),
    url(r'^list_algorithms', views.list_algorithms, name='list_algorithms'),

    url(r'^cold_start_all/$', views.cold_start_all, name='cold_start_all'),
    url(r'^cold_start_interest/$', views.cold_start_interest, name='cold_start_interest'),
    url(r'^cold_start_features/$', views.cold_start_features, name='cold_start_features'),

    url(r'^transition_components_based_ratings', views.transition_components_based_ratings,
        name='transition_components_based_ratings'),

    url(r'^transition_components_based_features', views.transition_components_based_features,
        name='transition_components_based_features'),
]
