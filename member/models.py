from administrator.models import Event
from django.db import models
from accounts.models import Profile
from administrator.models import Event

# Create your models here.


class EventRegistration(models.Model):

    APPROVAL = (
        ('APPROVED', 'APPROVED'),
        ('PENDING', 'PENDING'),
        ('REJECTED', 'REJECTED'),
    )

    user = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    receipt = models.ImageField(null=True, blank=True)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    is_registration_approved = models.CharField(
        max_length=200, null=True, choices=APPROVAL)
    time_of_attendance = models.DateTimeField(
        auto_now_add=False, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.user.username + "+" + self.event.event_name
