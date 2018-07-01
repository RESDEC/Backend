from django.contrib import admin
from .models import VariabilityEnvironment, RelationshipType, VariabilityEnvironmentData


# Register your models here.
admin.site.register(VariabilityEnvironment)
admin.site.register(RelationshipType)
admin.site.register(VariabilityEnvironmentData)
