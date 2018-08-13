from django.db import models
from django.contrib.auth.models import User


"""Status of objects in the system. If the object have a status 'Inactive', it not gonna take part
of the searching"""
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
    separator = models.CharField(max_length=1, default='|')
    item_column = models.CharField(max_length=20, default='')
    feature_column = models.CharField(max_length=20, default='')
    rating_column = models.CharField(max_length=20, default='')

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
    item_name = models.CharField(max_length=40, )

    def __str__(self):
        return self.item_name + " - " + self.interest.name.strip()


class HistoryUserItems(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    variability_environment = models.ForeignKey(VariabilityEnvironment, on_delete=models.CASCADE,)
    item_name = models.CharField(max_length=40)
    date_use = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user.first_name.strip() + " - " + self.variability_environment.name.strip() \
               + self.item_name.strip() + " - " + self.date_use.__str__()
