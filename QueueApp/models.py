from django.db import models
from UserApp.models import Citizen
from StaffApp.models import Staff
from AdminApp.models import Service


class QueueToken(models.Model):
    token_id = models.AutoField(primary_key=True)

    citizen = models.ForeignKey(
        Citizen,
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    token_number = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        default='Waiting'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'queue_token'

    def __str__(self):
        return self.token_number

