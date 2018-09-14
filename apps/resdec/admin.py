from django.contrib import admin
from .models import VariabilityEnvironment, RelationshipType, VariabilityEnvironmentData, \
    Algorithm, Interest, InterestItemsNames, HistoryUserItems, UserProfile


# Register your models here.
admin.site.register(VariabilityEnvironment)
admin.site.register(RelationshipType)
admin.site.register(VariabilityEnvironmentData)
admin.site.register(Interest)
admin.site.register(InterestItemsNames)
admin.site.register(Algorithm)
admin.site.register(HistoryUserItems)
admin.site.register(UserProfile)
