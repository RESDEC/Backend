from django.db import models


# Create your models here.
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
    file = models.FileField(upload_to='../resources/data/uploaded')
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name
