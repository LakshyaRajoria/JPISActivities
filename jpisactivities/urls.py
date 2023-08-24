from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib import admin
from main import views
from django.urls import path, include
from django.conf.urls import  url

app_name = 'jpisactivities'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.homepage),
    path('signup/',views.signup,name="signup"),
    path('activity-creation/',views.activity_creation,name="activity_creation"),
    path('signup-administrator/',views.administrator_signup,name="administrator_signup"),
    path('admin-page/',views.administrator_landing,name="admin_page"),
    path('remove-activity/<str:s>/',views.remove_activity,name="remove-activity"),
    path('student-page/',views.student_landing,name="student_land"),
    path('logout/',views.log_out,name="logout"),
    path('user/',views.user,name="user"),
    path('applications/<str:s>/',views.applications,name="applications"),
    path('catalog/',views.catalog,name="catalog"),
    path('catalog/<str:s>/activity-signup/',views.activity_signup,name="activity-signup"),
    path('catalog/<str:s>/activity-signup/leave/',views.activity_leave,name="activity-leave"),
    path('student-page/<str:s>/accept/', views.accept_request),
    path('student-page/<str:s>/reject/', views.reject_request),
    path('chat/', include('main.urls')),
    path('calendar-page/', include('calendarapp.urls')),
    path('all-meetings-info/',views.export_xls,name="export_xls"),
]
