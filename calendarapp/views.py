# cal/views.py

from datetime import datetime, date
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta
import calendar
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from main.models import *
from .models import *
from .utils import Calendar
from .forms import EventForm
from django.utils.timezone import is_aware, is_naive, make_naive, make_aware

import xlwt
from django.contrib.auth.models import User

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

class CalendarView(LoginRequiredMixin, generic.ListView):
    login_url = 'signup'
    model = Event
    template_name = 'calendar.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

class CalendarView2(LoginRequiredMixin, generic.ListView):
    login_url = 'signup'
    model = Event
    template_name = 'normal_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


@login_required(login_url='signup')
def create_event(request):
    form = EventForm(request.POST or None)
    activities = Organizations.objects.all().filter(leader1=request.user.username)

    user_activities = []
    for a in activities:
        user_activities.append(a.org_name)


    context = {
        'form': form,
        "activities":user_activities,
    }

    if request.POST and form.is_valid():
        activity = form.cleaned_data['activity']
        title = form.cleaned_data['title']
        date = form.cleaned_data['date']

        from datetime import datetime


        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            context.update({"error_message4": 'Please Input a Date Object in the Date Field in the Year-Month-Day Format'})
            return render(request, 'event.html', context)

        import datetime

        if activity not in user_activities:
            activity_not_there = True
            context.update({"activity_not_there": activity_not_there})

        else:
            description = form.cleaned_data['description']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            date = form.cleaned_data['date']
            Event.objects.get_or_create(
                user=request.user,
                activity=activity,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                date=date,
            )

            return HttpResponseRedirect(reverse('calendarapp:calendar'))
    return render(request, 'event.html', context)

class EventEdit(generic.UpdateView):
    model = Event
    fields = ['description', 'start_time', 'end_time']
    template_name = 'event.html'

@login_required(login_url='signup')
def event_details(request, event_id):

    event = Event.objects.get(id=event_id)

    context = {
        'event': event,
    }
    return render(request, 'event-details.html', context)
