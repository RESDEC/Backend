from django.db import models
from ResdecSolution.settings import BASE_DIR

"""Status of objects in the system. If the object have a status 'Inactive', it not gonna take part
of the searchings"""
ACTIVE = "A"
INACTIVE = "I"


STATUS = [(ACTIVE, "Active"),
          (INACTIVE, "Inactive"),
          ]

"""Data files (csv), can be based on two different types"""
FEATURES = 'F'
RATINGS = 'R'

BASE_ON = [(FEATURES, "Features"),
       (RATINGS, "Ratings")
       ]


class VariabilityEnvironment(models.Model):
    name = models.CharField(max_length=40)
    status = models.CharField(choices=STATUS, max_length=1, default='A')

    def __str__(self):
        return self.name


class RelationshipType(models.Model):
    name = models.CharField(max_length=40)
    status = models.CharField(choices=STATUS, max_length=1, default='A')

    def __str__(self):
        return self.name


class VariabilityEnvironmentData(models.Model):
    variability_environment = models.ForeignKey(VariabilityEnvironment, on_delete=models.CASCADE)
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE)
    base_on = models.CharField(choices=BASE_ON, max_length=1, default='')
    name = models.CharField(max_length=40)
    extension = models.CharField(max_length=4)
    size = models.IntegerField(default=0)
    number_records = models.IntegerField(default=0)
    file = models.FileField(upload_to="user_data_uploaded", max_length=500)
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=1, default='A')

    def __str__(self):
        return self.name


class Algorithm(models.Model):
    name = models.CharField(max_length=40)
    status = models.CharField(choices=STATUS, max_length=1, default='A')
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Interest(models.Model):
    name = models.CharField(max_length=40)
    status = models.CharField(choices=STATUS, max_length=1, default='A')
    variability_environment = models.ForeignKey(VariabilityEnvironment, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class InterestItemsNames(models.Model):
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=40,)

    def __str__(self):
        return self.item_name + " - " + self.interest.name
