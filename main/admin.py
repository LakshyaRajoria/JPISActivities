from django.contrib import admin
#above line is new
# Register your models here.
from .models import *
# Register your models here.

class Admin(admin.ModelAdmin):
    pass

admin.site.register(Accounts,Admin)
admin.site.register(Organizations,Admin)
admin.site.register(JoinRequests,Admin)
admin.site.register(Message,Admin)
