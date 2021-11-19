from django.forms import ModelForm
from django import forms
from .models import *


class EventRegistrationForm(ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['receipt', 'is_registration_approved']

    def __init__(self, *args, **kwargs):
        super(EventRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['is_registration_approved'].widget.attrs.update(
            {'class': 'form-control', 'required': 'required'})
        self.fields['receipt'].widget.attrs.update(
            {'class': 'form-control upload-image-receipt'})
