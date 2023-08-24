from django.urls import path

from . import views

app_name = 'calendarapp'
urlpatterns = [
    path('normal-calendar', views.CalendarView.as_view(), name='calendar'),
    path('normal-calendar2', views.CalendarView2.as_view(), name='calendar2'),
    path('event/new/', views.create_event, name='event_new'),
    path('event/edit/<int:pk>/', views.EventEdit.as_view(), name='event_edit'),
    path('event/<int:event_id>/details/', views.event_details, name='event-detail'),

]
