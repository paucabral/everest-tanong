from django.forms.fields import NullBooleanField
import django_filters
from django_filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from .models import *
from django import forms
from administrator.models import *
from django.db.models import Q


class FindEventFilter(django_filters.FilterSet):
    search_fields = CharFilter(method='custom_search_filter', label="Search")

    class Meta:
        model = Event
        fields = ['search_fields', 'event_name', 'short_description', 'detailed_description',
                  'is_registration_open', 'is_attendance_open', 'price', 'cost', 'event_type']

    def custom_search_filter(self, queryset, name, value):
        return Event.objects.filter(
            Q(event_name__icontains=value) | Q(short_description__icontains=value) | Q(detailed_description__icontains=value))


class EventsJoinedFilter(django_filters.FilterSet):
    search_fields = CharFilter(method='custom_search_filter', label="Search")
    cost = ChoiceFilter(field_name='event__cost', choices=Event.EVENT_COST)
    event_type = ChoiceFilter(field_name='event__event_type',
                              choices=Event.EVENT_TYPE)
    approval = ChoiceFilter(field_name='is_registration_approved',
                            choices=EventRegistration.APPROVAL)

    attendance = ModelChoiceFilter(
        field_name='time_of_attendance', lookup_expr='isnull',
        null_label='ABSENT',
        queryset=EventRegistration.objects.all(),
    )

    CHOICES = (('', '-------'),
               (True, 'PRESENT'), (False, 'ABSENT'))
    attendance_bool = django_filters.BooleanFilter(
        field_name='time_of_attendance', lookup_expr='isnull', exclude=True, widget=forms.Select(choices=CHOICES))

    class Meta:
        model = EventRegistration
        fields = ['attendance_bool', 'attendance', 'search_fields', 'user', 'event',
                  'is_registration_approved', 'time_of_attendance']

    def custom_search_filter(self, queryset, name, value):
        return EventRegistration.objects.filter(
            Q(event__event_name__icontains=value) | Q(event__short_description__icontains=value) | Q(event__detailed_description__icontains=value))
