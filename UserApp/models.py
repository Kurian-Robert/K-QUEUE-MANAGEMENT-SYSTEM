from django.db import models


class Citizen(models.Model):
    citizen_id = models.AutoField(primary_key=True)
    citizen_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=80, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'citizen'

    def __str__(self):
        return self.citizen_name