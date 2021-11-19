from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.


class Event(models.Model):
    EVENT_TYPE = (
        ('CONFERENCE', 'CONFERENCE'),
        ('SEMINAR', 'SEMINAR'),
        ('WORKSHOP', 'WORKSHOP'),
    )

    EVENT_COST = (
        ('FREE', 'FREE'),
        ('PAID', 'PAID'),
    )

    event_name = models.CharField(max_length=200, null=True)
    short_description = models.CharField(max_length=200, null=True)
    detailed_description = RichTextField(blank=True, null=True)
    event_type = models.CharField(
        max_length=200, null=True, choices=EVENT_TYPE)
    date = models.DateTimeField(auto_now_add=False, null=True)
    location = models.CharField(max_length=200, null=True)
    is_registration_open = models.BooleanField(null=False)
    is_attendance_open = models.BooleanField(null=False)
    cost = models.CharField(
        max_length=200, null=True, choices=EVENT_COST)
    price = models.DecimalField(max_digits=19, decimal_places=2)

    def __str__(self):
        return self.event_name


class SupportContact(models.Model):
    CONTACT_TYPE = (
        ('EMAIL', 'EMAIL'),
        ('NUMBER', 'NUMBER'),
    )

    support_contact = models.CharField(max_length=200, null=True)
    contact_type = models.CharField(
        max_length=200, null=True, choices=CONTACT_TYPE)

    def __str__(self):
        return self.support_contact


class Banner(models.Model):
    POSITION = (
        ('1ST BANNER', '1ST BANNER'),
        ('2ND BANNER', '2ND BANNER'),
        ('3RD BANNER', '3RD BANNER'),
    )

    position = models.CharField(
        max_length=200, null=True, choices=POSITION)
    banner_img = models.ImageField(null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
