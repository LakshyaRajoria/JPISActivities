from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=120)
    title = models.CharField(max_length=200)
    start_time =  models.DateTimeField()
    end_time = models.DateTimeField()
    date = models.CharField(default=date.today(),  max_length=120)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('calendarapp:event-detail', args=(self.id,))

    @property
    def get_html_url(self):
        url = reverse('calendarapp:event-detail', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
