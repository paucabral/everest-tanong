from django.db.models import query
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from administrator.models import Event, SupportContact
from .models import *
from .filters import *
from django.contrib import messages
from django.utils import timezone
import datetime
from .forms import EventRegistrationForm
from member.models import Event, EventRegistration

# Create your views here.


class MemberDashboard(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        user = Profile.objects.get(id=request.user.profile.id)
        registered_events = EventRegistration.objects.filter(
            user=user).order_by("-date_created")[:10]

        approved = EventRegistration.objects.filter(user=user).filter(
            is_registration_approved='APPROVED').count()
        pending = EventRegistration.objects.filter(user=user).filter(
            is_registration_approved='PENDING').count()
        rejected = EventRegistration.objects.filter(user=user).filter(
            is_registration_approved='REJECTED').count()

        banner1 = Banner.objects.filter(
            position="1ST BANNER")
        if not banner1:
            banner1 = None
        else:
            banner1 = Banner.objects.filter(
                position="1ST BANNER").latest('date_added')

        banner2 = Banner.objects.filter(
            position="2ND BANNER")
        if not banner2:
            banner2 = None
        else:
            banner2 = Banner.objects.filter(
                position="2ND BANNER").latest('date_added')

        banner3 = Banner.objects.filter(
            position="3RD BANNER")
        if not banner3:
            banner3 = None
        else:
            banner3 = Banner.objects.filter(
                position="3RD BANNER").latest('date_added')
        return render(request, template_name='member/dashboard.html', context={'banner1': banner1, 'banner2': banner2, 'banner3': banner3, 'registered_events': registered_events, 'approved': approved, 'pending': pending, 'rejected': rejected})


class FindEvent(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(
            is_registration_open=True).order_by('date')
        user = Profile.objects.get(id=request.user.profile.id)
        user_registered_events_approved = EventRegistration.objects.filter(
            user=user).filter(is_registration_approved='APPROVED').values_list('event_id', flat=True)
        user_registered_events_pending = EventRegistration.objects.filter(
            user=user).filter(is_registration_approved='PENDING').values_list('event_id', flat=True)
        user_registered_events_rejected = EventRegistration.objects.filter(
            user=user).filter(is_registration_approved='REJECTED').values_list('event_id', flat=True)

        find_event_filter = FindEventFilter(request.GET, queryset=events)
        events = find_event_filter.qs

        return render(request, template_name='member/find-event.html', context={'events': events, 'user_registered_events_approved': user_registered_events_approved, 'user_registered_events_pending': user_registered_events_pending, 'user_registered_events_rejected': user_registered_events_rejected, 'find_event_filter': find_event_filter})


class ViewEvent(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)
        user = Profile.objects.get(id=request.user.profile.id)

        support_contacts_email = SupportContact.objects.filter(
            contact_type='EMAIL').values_list('support_contact', flat=True)
        support_contacts_number = SupportContact.objects.filter(
            contact_type='NUMBER').values_list('support_contact', flat=True)

        user_registered_events_approved = EventRegistration.objects.filter(
            user=user).filter(is_registration_approved='APPROVED').values_list('event_id', flat=True)
        user_registered_events_pending = EventRegistration.objects.filter(
            user=user).filter(is_registration_approved='PENDING').values_list('event_id', flat=True)
        user_registered_events_rejected = EventRegistration.objects.filter(
            user=user).filter(is_registration_approved='REJECTED').values_list('event_id', flat=True)

        user_confirmed_attendance = EventRegistration.objects.filter(
            user=user).filter(event=event).exclude(time_of_attendance__isnull=True).values_list('event_id', flat=True)

        return render(request, template_name='member/event-details.html', context={'event': event, 'user_registered_events_approved': user_registered_events_approved, 'user_registered_events_pending': user_registered_events_pending, 'user_registered_events_rejected': user_registered_events_rejected, 'support_contacts_email': support_contacts_email, 'support_contacts_number': support_contacts_number, 'user_confirmed_attendance': user_confirmed_attendance})


@login_required(login_url='/')
def registerEvent(request, event_id):
    if request.method == "POST":
        user = Profile.objects.get(id=request.user.profile.id)
        event = Event.objects.get(id=event_id)
        time = timezone.now()

        if event.cost == "FREE":
            approval = 'APPROVED'
            new_event_registration = EventRegistration.objects.create(
                user=user, event=event, is_registration_approved=approval)

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'You have successfully registered on the event.')
            return redirect("/member/events/event/{}".format(event_id))

        else:
            return redirect('/member/events/event/register/form/{}'.format(event_id))


@login_required(login_url='/')
def unregisterEvent(request, event_id):
    if request.method == "POST":
        user = Profile.objects.get(id=request.user.profile.id)
        event = Event.objects.get(id=event_id)

        event_registered = EventRegistration.objects.filter(
            user=user, event=event)

        event_registered.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'You have successfully unregistered from the event.')
        return redirect("/member/events/event/{}".format(event_id))


@login_required(login_url='/')
def confirmAttendance(request, event_id):
    if request.method == "POST":
        user = Profile.objects.get(id=request.user.profile.id)
        event = Event.objects.get(id=event_id)

        event_registered = EventRegistration.objects.get(
            user=user, event=event)

        event_registered.time_of_attendance = timezone.now()
        event_registered.save()

        messages.add_message(request,
                             messages.SUCCESS,
                             'Yor attendance was recorded successfully.')
        return redirect("/member/events/event/{}".format(event_id))


class PaidRegistration(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)
        user = Profile.objects.get(id=request.user.profile.id)

        form = EventRegistrationForm()

        user_registered_event = EventRegistration.objects.filter(
            user=user).filter(event=event_id).values_list('event_id', flat=True)

        return render(request, template_name='member/paid-registration-form.html', context={'form': form, 'user_registered_event': user_registered_event, 'user': user, 'event': event})

    @method_decorator(login_required(login_url='/'))
    def post(self, request, *args, **kwargs):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)
        user = Profile.objects.get(id=request.user.profile.id)
        approval = "PENDING"

        receipt = request.FILES['receipt']

        event_reg = EventRegistration.objects.create(
            user=user, receipt=receipt, event=event, is_registration_approved=approval)
        event_reg.save()

        messages.add_message(request,
                             messages.SUCCESS,
                             'Your receipt/proof of payment was submitted successfully.')
        return redirect("/member/events/event/{}".format(event_id))


class EventsJoined(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        user = Profile.objects.get(id=request.user.profile.id)
        user_registered_events = EventRegistration.objects.filter(user=user)

        joined_events_filter = EventsJoinedFilter(
            request.GET, queryset=user_registered_events)
        user_registered_events = joined_events_filter.qs

        return render(request, template_name='member/events-joined.html', context={'user_registered_events': user_registered_events, 'joined_events_filter': joined_events_filter})


class Transactions(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        user = Profile.objects.get(id=request.user.profile.id)
        transactions = EventRegistration.objects.filter(
            user=user).order_by('-date_created')

        transactions_filter = EventsJoinedFilter(
            request.GET, queryset=transactions)
        transactions = transactions_filter.qs

        return render(request, template_name='member/transactions.html', context={'transactions': transactions, 'transactions_filter': transactions_filter})
