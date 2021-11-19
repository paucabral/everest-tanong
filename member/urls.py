from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard', views.MemberDashboard.as_view(),
         name='member-dashboard'),
    path('events/find', views.FindEvent.as_view(),
         name='find-event'),
    path('events/event/<int:event_id>', views.ViewEvent.as_view(),
         name='view-event'),
    path('events/event/register/<int:event_id>',
         views.registerEvent, name='register-event'),
    path('events/event/unregister/<int:event_id>',
         views.unregisterEvent, name='unregister-event'),
    path('events/event/confirm-attendance/<int:event_id>',
         views.confirmAttendance, name='confirm-attendance'),
    path('events/event/register/form/<int:event_id>', views.PaidRegistration.as_view(),
         name='paid-registration'),
    path('events/joined', views.EventsJoined.as_view(),
         name='find-event'),
    path('transactions', views.Transactions.as_view(),
         name='transactions'),
]
