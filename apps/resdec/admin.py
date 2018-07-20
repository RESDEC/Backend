from django.contrib import admin
from .models import VariabilityEnvironment, RelationshipType, VariabilityEnvironmentData, Trend, TrendsItemsNames, Algorithm


# Register your models here.
admin.site.register(VariabilityEnvironment)
admin.site.register(RelationshipType)
admin.site.register(VariabilityEnvironmentData)
admin.site.register(Trend)
admin.site.register(TrendsItemsNames)
admin.site.register(Algorithm)
