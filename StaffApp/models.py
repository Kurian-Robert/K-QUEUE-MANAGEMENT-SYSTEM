from django.db import models
from AdminApp.models import Department


class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    staff_name = models.CharField(max_length=60)
    role = models.CharField(max_length=30, default='Staff')

    class Meta:
        db_table = 'staff'

    def __str__(self):
        return self.staff_name