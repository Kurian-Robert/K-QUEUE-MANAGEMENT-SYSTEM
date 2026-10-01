from django.db import models
from django.contrib.auth.models import User,AbstractUser
# Create your models here.
class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True,max_length=100)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    picture = models.ImageField(upload_to='admin_pics')

    class Meta:
        db_table = 'admin'


class Office(models.Model):
    office_id = models.AutoField(primary_key=True)
    office_name = models.CharField(max_length=80)
    office_type = models.CharField(max_length=40)
    district = models.CharField(max_length=40)

    class Meta:
        db_table = 'office'

    def __str__(self):
        return self.office_name


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)

    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.department_name

class Service(models.Model):
    service_id = models.AutoField(primary_key=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    service_name = models.CharField(max_length=60)
    avg_service_min = models.SmallIntegerField()

    class Meta:
        db_table = 'service'

    def __str__(self):
        return self.service_name