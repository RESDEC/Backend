from django.db import models
from ResdecSolution.settings import BASE_DIR

ACTIVE = "A"
INACTIVE = "I"


STATUS = [(ACTIVE, "Active"),
          (INACTIVE, "Inactive"),
          ]


class VariabilityEnvironment(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class RelationshipType(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class VariabilityEnvironmentData(models.Model):
    variability_environment = models.ForeignKey(VariabilityEnvironment, on_delete=models.CASCADE)
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    path = models.CharField(max_length=80, default="")
    extension = models.CharField(max_length=4)
    size = models.IntegerField(default=0)
    number_records = models.IntegerField(default=0)
    file = models.FileField(upload_to="user_data_uploaded", max_length=500)
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=1, default='')

    def __str__(self):
        return self.name


class Algorithm(models.Model):
    name = models.CharField(max_length=40)
    status = models.CharField(choices=STATUS, max_length=1)
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Trend(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class TrendsItemsNames(models.Model):
    trend = models.ForeignKey(Trend, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=40,)
    status = models.CharField(choices=STATUS, max_length=1)
