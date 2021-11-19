from member.views import Transactions
from member.forms import EventRegistrationForm
from django.core.exceptions import EmptyResultSet
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .decorators import *
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from accounts.models import Profile, User
from django.db.models import Q
from member.models import Event, EventRegistration
from member.filters import FindEventFilter, EventsJoinedFilter
import datetime
from datetime import timedelta

# Create your views here.


class AdministratorDashboard(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
        approved = EventRegistration.objects.filter(
            is_registration_approved='APPROVED').count()
        pending = EventRegistration.objects.filter(
            is_registration_approved='PENDING').count()
        rejected = EventRegistration.objects.filter(
            is_registration_approved='REJECTED').count()
        recent = EventRegistration.objects.order_by('-date_created')[:20]

        today_min = datetime.datetime.combine(
            datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(
            datetime.date.today(), datetime.time.max)
        today = Event.objects.filter(
            date__range=(today_min, today_max))

        this_day = datetime.datetime.today()
        upcoming = Event.objects.filter(
            date__gte=this_day).order_by('date')

        previous = Event.objects.filter(date__lte=this_day).exclude(
            date__range=(today_min, today_max)).order_by('-date')[:5]

        event_objs = Event.objects.order_by('-date')[:10]

        events = []
        registered = []
        attended = []

        for i in event_objs:
            events.append(i.event_name)

            user_confirmed_attendance = EventRegistration.objects.filter(
                event=i).filter(
                is_registration_approved='APPROVED').count()
            registered.append(user_confirmed_attendance)

            user_confirmed_attendance = EventRegistration.objects.filter(event=i).exclude(
                time_of_attendance__isnull=True).count()
            attended.append(user_confirmed_attendance)
        return render(request, template_name='administrator/dashboard.html', context={'approved': approved, 'pending': pending, 'rejected': rejected, 'recent': recent, 'today': today, 'upcoming': upcoming, 'previous': previous, 'events': events, 'registered': registered, 'attended': attended})


class CreateEvent(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
        form = EventForm()
        return render(request, template_name='administrator/event-form.html', context={'form': form})

    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def post(self, request, *args, **kwargs):
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'The event was added successfully.')
            return redirect('/administrator/events/list')
        else:
            messages.error(request, 'The event was not added due to an error.')
            return render(request, template_name='administrator/event-form.html', context={'form': form})


class UpdateEvent(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)

        form = EventForm(instance=event)
        return render(request, template_name='administrator/event-form.html', context={'form': form})

    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def post(self, request, *args, **kwargs):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)

        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'The event was updated successfully.')
            return redirect('/administrator/events/event/{}/reports'.format(event_id))
        else:
            messages.error(
                request, 'The event was not updated due to an error.')
            return render(request, template_name='administrator/event-form.html', context={'form': form})


class ListEvents(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
        events = Event.objects.all().order_by('-date')

        find_event_filter = FindEventFilter(request.GET, queryset=events)
        events = find_event_filter.qs

        return render(request, template_name='administrator/list-events.html', context={'events': events, 'find_event_filter': find_event_filter})


@login_required(login_url='/')
@admin_only()
def deleteEvent(request, event_id):
    if request.method == "POST":
        event = Event.objects.filter(id=event_id)
        event.delete()

        messages.add_message(request,
                             messages.SUCCESS,
                             'The event was deleted successfully.')
        return redirect('/administrator/events/list')

    return redirect('/administrator/events/list')


class ListMembers(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
        registered_events = EventRegistration.objects.exclude(
            time_of_attendance__isnull=True)

        members = User.objects.exclude(
            Q(is_superuser=True)).order_by('first_name')
        return render(request, template_name='administrator/list-members.html', context={'members': members, 'registered_events': registered_events})


@login_required(login_url='/')
@admin_only()
def deleteMember(request, member_id):
    if request.method == "POST":
        user = User.objects.filter(id=member_id)
        user.delete()

        messages.add_message(request,
                             messages.SUCCESS,
                             'The user was deleted successfully.')
        return redirect('/administrator/members/list')

    return redirect('/administrator/members/list')


class AllTransactions(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        transactions = EventRegistration.objects.all().order_by('-date_created')

        transactions_filter = EventsJoinedFilter(
            request.GET, queryset=transactions)
        transactions = transactions_filter.qs

        return render(request, template_name='administrator/transactions.html', context={'transactions': transactions, 'transactions_filter': transactions_filter})


class SetTransactionStatus(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        transaction_id = self.kwargs['transaction_id']
        transaction = EventRegistration.objects.get(pk=transaction_id)

        form = EventRegistrationForm(instance=transaction)

        return render(request, template_name='administrator/set-transaction-status.html', context={'transaction': transaction, 'form': form})

    @method_decorator(login_required(login_url='/'))
    def post(self, request, *args, **kwargs):
        transaction_id = self.kwargs['transaction_id']
        transaction = EventRegistration.objects.get(pk=transaction_id)

        form = EventRegistrationForm(
            request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            form.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Transaction ID: {} was updated successfully.'.format(transaction_id))
            return redirect('/administrator/transactions')
        else:
            messages.error(
                request, 'Transaction ID: {} was not updated due to an error.'.format(transaction_id))
            return redirect('/administrator/transactions')


class EventReports(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)

        user_registered_events = EventRegistration.objects.filter(event=event)

        user_registered_events_approved = EventRegistration.objects.filter(
            is_registration_approved='APPROVED')
        user_registered_events_pending = EventRegistration.objects.filter(
            is_registration_approved='PENDING')
        user_registered_events_rejected = EventRegistration.objects.filter(
            is_registration_approved='REJECTED')

        user_confirmed_attendance = EventRegistration.objects.filter(event=event).exclude(
            time_of_attendance__isnull=True).values_list('event_id', flat=True)

        transactions_filter = EventsJoinedFilter(
            request.GET, queryset=user_registered_events)
        user_registered_events = transactions_filter.qs

        registered = user_registered_events_approved.filter(event=event).filter(
            is_registration_approved='APPROVED').count()

        attended = user_registered_events_approved.filter(event=event).filter(
            is_registration_approved='APPROVED').exclude(
            time_of_attendance__isnull=True).count()

        return render(request, template_name='administrator/event-reports.html', context={'transactions_filter': transactions_filter, 'user_registered_events': user_registered_events, 'event': event, 'user_registered_events_approved': user_registered_events_approved, 'user_registered_events_pending': user_registered_events_pending, 'user_registered_events_rejected': user_registered_events_rejected, 'user_confirmed_attendance': user_confirmed_attendance, 'registered': registered, 'attended': attended})


class MemberProfile(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        user = self.kwargs['member_id']
        profile = Profile.objects.get(user=user)

        user_attended_events = EventRegistration.objects.filter(
            user=profile).exclude(time_of_attendance__isnull=True)

        transactions = EventRegistration.objects.filter(user=profile)

        return render(request, template_name='administrator/user-profile.html', context={'profile': profile, 'user_attended_events': user_attended_events, 'transactions': transactions})


class SupportContacts(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
        support_contacts = SupportContact.objects.all()
        support_contact_submit = ContactForm()
        return render(request, template_name='administrator/support-contacts.html', context={'support_contacts': support_contacts, 'support_contact_submit': support_contact_submit})

    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'The contact information was added successfully.')
            return redirect("/administrator/support-contacts")

        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'There was error in adding the submitted contact information.')

        return redirect("/administrator/support-contacts")


@login_required(login_url='/')
@admin_only()
def deleteContact(request, contact_id):
    if request.method == "POST":
        contact = SupportContact.objects.filter(id=contact_id)
        contact.delete()

        messages.add_message(request,
                             messages.SUCCESS,
                             'The contact information was deleted successfully.')
        return redirect('/administrator/support-contacts')

    return redirect('/administrator/support-contacts')


class Announcement(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
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

        form = BannerForm()
        return render(request, template_name='administrator/banner.html', context={'form': form, 'banner1': banner1, 'banner2': banner2, 'banner3': banner3})

    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def post(self, request, *args, **kwargs):
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'The announcement banner was added successfully.')
            return redirect("/administrator/announcements")

        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'There was error in adding the announcement banner.')

        return redirect("/administrator/announcements")
