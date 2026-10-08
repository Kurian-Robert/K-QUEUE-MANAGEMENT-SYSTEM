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


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    token = models.OneToOneField(
        QueueToken,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    citizen = models.ForeignKey(
        Citizen,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(help_text="Rating between 1 and 5")
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'

    def __str__(self):
        return f"Feedback #{self.feedback_id} - Rating {self.rating}"

