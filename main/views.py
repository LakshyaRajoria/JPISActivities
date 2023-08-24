#importing all the required libraries
from django.http import JsonResponse
from django.contrib.auth.models import User
import os
import random
import uuid
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect
from .models import *
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
import json
from calendarapp.models import *
from django.utils import timezone
from datetime import timedelta
from datetime import datetime, date
from django.utils.timezone import is_aware, is_naive, make_naive, make_aware
import smtplib as sl
from django.core.mail import EmailMessage
import xlwt
from django.http import HttpResponse
from django.conf import settings
import pytz


#chat system
def index(request):
    return render(request, 'chat/index.html', {})

@login_required
def room(request, room_name):
    try:
        leader_organizations = Organizations.objects.all().filter(leader1=request.user.username, approved=True)
        leader_organizations_list = []
        leader_organizations_list1 = []
        for a in leader_organizations:
            leader_organizations_list.append(a.org_name)
            leader_organizations_list1.append(a.org_name)
        if room_name == leader_organizations[0].org_name:
            leader_organizations_list = leader_organizations_list[1:]
    except:
        pass

    try:
        member_organizations = JoinRequests.objects.all().filter(username=request.user.username, approved=True)
        member_organizations_list = []
        member_organizations_list1 = []

        for b in member_organizations:
            member_organizations_list.append(b.org_name)
            member_organizations_list1.append(b.org_name)
        if room_name == member_organizations[0].org_name:
            member_organizations_list = member_organizations_list[1:]

    except:
        pass

    if (room_name not in leader_organizations_list1) and (room_name not in member_organizations_list1):
        return HttpResponseForbidden("No such room exists or you don't have permission to access this room. Please navigate back")
    #display both groups in one array
    all_channels = leader_organizations_list + member_organizations_list

    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'all_channels': all_channels,
        'room_name': room_name,
        'username': mark_safe(json.dumps(request.user.username)),
    })


#----------Main system----------
def homepage(request):
	#----------login authentication----------
    context = {
        "action":request.POST.get('action'),
		"username":request.POST.get('username'),
        "password":request.POST.get('psw'),
        }
    message = ""
    if context["action"] == "sub":
        user =  authenticate(request,username=context["username"], password=context["password"])
        if user is None:
            message = "Wrong Username or Password"
            context.update({"message":message})
        elif user is not None:
            login(request,user)
            return HttpResponseRedirect('/user/')
    #----------end of login authentication----------

    if request.user.is_authenticated:
        context.update({ "user": request.user.username})
    if not(request.user.is_authenticated):
        context.update({ "not_authenthicated": True})
    return render(request,'homepage.html',context)




def log_out(request):
    logout(request)
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')


def signup(request):
    context = {
        "action":request.POST.get('action'),
        "email":request.POST.get('email'),
		"grade":request.POST.get('grade'),
        "first_name":request.POST.get('first_name'),
		"last_name":request.POST.get('last_name'),
        "psw":request.POST.get('psw'),
        "psw-repeat":request.POST.get('psw-repeat'),
    }
    email = context["email"]
    if context["action"] == "sub" and context['psw'] == context['psw-repeat'] and (email[email.index("@"):] == '@jpischool.com' or email == "jpisactivities2@gmail.com"):
        Accounts.objects.create(f_name=(context["first_name"]), l_name=(context["last_name"]),email=context["email"], grade=context["grade"],student=True)
        user = User.objects.create_user(request.POST.get("username", None), request.POST.get("email", None), request.POST.get("psw", None))
        user.first_name = request.POST.get("first_name", None)
        user.last_name = request.POST.get("last_name", None)
        user.save()
        login(request,user)
        return HttpResponseRedirect('/student-page/')
    elif context["action"] == "sub" and email[email.index("@"):] != '@jpischool.com' and email != "jpisactivities2@gmail.com":
        context.update({"error_message1": 'Please Enter a School Email.'})
    elif context["action"] == "sub" and context['psw'] != context['psw-repeat']:
        context.update({"error_message2": 'Inputted Passwords Do Not Match.'})

    return render(request,'g_signup.html',context)


def activity_creation(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.user.is_authenticated:
        user_identification = Accounts.objects.all().filter(email=request.user.email)
        if user_identification[0].administrator == True:
            return HttpResponseRedirect('/user/')

    context = {
        "action":request.POST.get('action'),
        "org_name":request.POST.get('org_name'),
        "email":request.POST.get('email'),
        "tag1":request.POST.get('tag1'),
        "commitment":request.POST.get('commitment'),
        "num_times":request.POST.get('num_times'),
        "leader1":request.POST.get('leader1'),
        "mission_statement":request.POST.get('mission_statement'),
        "description":request.POST.get('description'),
        "protocols":request.POST.get('protocols'),
        "advisor": request.POST.get('advisor'),
    }


    tag2 = request.POST.get('tag2')
    tag3 = request.POST.get('tag3')
    leader2 = request.POST.get('leader2')
    leader3 = request.POST.get('leader3')
    leader4 = request.POST.get('leader4')
    other_leaders = []
    if leader2:
        other_leaders.append(leader2)
    if leader3:
        other_leaders.append(leader3)
    if leader4:
        other_leaders.append(leader4)


    def un_spacify(param):
        if ' ' in param:
            param = param.split(' ')
            param_temp = ''
            for i in param:
                param_temp += i
            param = param_temp
        return param

    try:
        if context["action"] == "sub" and int(context["num_times"]):
            activity_name = context["org_name"]
            context.update({"org_name": un_spacify(str(activity_name))})

            for leader in other_leaders:
                username_var = un_spacify(str(leader))
                JoinRequests.objects.create(org_name=context["org_name"], first_name=leader, last_name='N/A', username=username_var, grade=Accounts.objects.all().filter(email=request.user.email)[0].grade, interest_shown="Yes", num_activities_in=0, approved=True)

            if context['commitment'] == 'low':
                Organizations.objects.create(org_name=context["org_name"],email=context['email'],tag1=context['tag1'],tag2=tag2,tag3=tag3, advisor_name= context['advisor'], low=True, num_times=context['num_times'], leader1=context['leader1'], leader2=leader2, leader3=leader3, leader4=leader4, mission_statement=context['mission_statement'], description=context['description'], protocols=context['protocols'])
            elif context['commitment'] == 'medium':
                Organizations.objects.create(org_name=context["org_name"],email=context['email'],tag1=context['tag1'],tag2=tag2,tag3=tag3, advisor_name= context['advisor'], medium=True, num_times=context['num_times'], leader1=context['leader1'], leader2=leader2, leader3=leader3, leader4=leader4, mission_statement=context['mission_statement'], description=context['description'], protocols=context['protocols'])
            elif context['commitment'] == 'high':
                Organizations.objects.create(org_name=context["org_name"],email=context['email'],tag1=context['tag1'],tag2=tag2,tag3=tag3, advisor_name= context['advisor'], high=True, num_times=context['num_times'], leader1=context['leader1'], leader2=leader2, leader3=leader3, leader4=leader4, mission_statement=context['mission_statement'], description=context['description'], protocols=context['protocols'])
            return redirect('../student-page/')
    except ValueError:
        context.update({"error_message3": 'Please Input an integer value for the number of meetings in a week.'})
        return render(request, 'activity_creation.html', context)

    return render(request, 'activity_creation.html', {})


def user(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    user_email_identification = Accounts.objects.all().filter(email=request.user.email)[0]
    user_administrator_test = Accounts.objects.all().filter(administrator=True)
    user_student_test = Accounts.objects.all().filter(student=True)
    administrator_test = []
    student_test = []

    for x in user_administrator_test:
    	administrator_test.append(x)
    for y in user_student_test:
    	student_test.append(y)
    if user_email_identification in administrator_test:
    	return redirect('../admin-page/')
    elif user_email_identification in student_test:
    	return redirect('../student-page/')


def administrator_signup(request):
    context = {
        "action":request.POST.get('action'),
        "email":request.POST.get('email'),
		"first_name":request.POST.get('first_name'),
		"last_name":request.POST.get('last_name'),
		"username":request.POST.get('username'),
        "psw":request.POST.get('psw'),
        "psw-repeat":request.POST.get('psw-repeat'),
    }
    if context["action"] == "sub" and context['psw'] == context['psw-repeat']:
        Accounts.objects.create(f_name=(context["first_name"]), l_name=(context["last_name"]),email=context["email"],grade=None,administrator=True)
        user = User.objects.create_user(request.POST.get("username", None), request.POST.get("email", None), '')
        user.first_name = request.POST.get("first_name", None)
        user.last_name = request.POST.get("last_name", None)
        user.save()
        login(request,user)
        return HttpResponseRedirect('/admin-page/')
    return render(request, 'administrator_signup.html')



def administrator_landing(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.user.is_authenticated:
        user_identification = Accounts.objects.all().filter(email=request.user.email)
        if user_identification[0].student == True:
            return HttpResponseRedirect('/user/')


    context = {
        "unapproved_applications": Organizations.objects.all().filter(approved=False, rejected=False),
        "approved_applications": Organizations.objects.all().filter(approved=True),
        }

    return render(request, 'administrator_landing.html', context)

def remove_activity(request, s):
    organization = Organizations.objects.all().filter(id=s)[0]
    obj = get_object_or_404(Organizations, org_name=organization.org_name)
    obj.delete()
    try:
        join_requests = JoinRequests.objects.all().filter(org_name = organization.org_name)[0]
        obj2 = get_object_or_404(JoinRequests, org_name=join_requests.org_name)
        obj2.delete()
        return HttpResponseRedirect('/user/')
    except:
        return HttpResponseRedirect('/user/')

def accept_request(request,s):
    JoinRequests.objects.all().filter(id=s).update(approved=True)
    return HttpResponseRedirect('/')
def reject_request(request,s):
    JoinRequests.objects.all().filter(id=s).update(rejected=True)
    return HttpResponseRedirect('/')

def student_landing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.user.is_authenticated:
        user_identification = Accounts.objects.all().filter(email=request.user.email)
        if user_identification[0].administrator == True:
            return HttpResponseRedirect('/user/')


    try:


        proposal_accepted_qset = Organizations.objects.all().filter(leader1=request.user.username)
        proposal_accepted_list = []
        for i in proposal_accepted_qset:
            if i.approved == True:
                proposal_accepted_list.append(i)

        proposal_denied_qset = Organizations.objects.all().filter(leader1=request.user.username)
        proposal_denied_list = []
        for j in proposal_denied_qset:
            if j.rejected == True:
                proposal_denied_list.append(j)

        context = {
            "proposal_accepted": proposal_accepted_list,
            "proposal_denied": proposal_denied_list,
            "num_join_requests_sent": len(JoinRequests.objects.all().filter(username=request.user.username))
        }

        if proposal_accepted_list:
            #this gets me the activity that the this user made and all the requests for that activity
            querysets = []
            for organization in proposal_accepted_list:
                if JoinRequests.objects.all().filter(org_name=organization.org_name, approved=False, rejected=False):
                    querysets.append(JoinRequests.objects.all().filter(org_name=organization.org_name, approved=False, rejected=False))
            #if none of the organization they have has any join requests
            context.update({ "querysets": querysets})
            if len(querysets) == 0:
                no_join_requests = True
                context.update({"no_join_requests": no_join_requests})

        #doesn't have any organization that has been accepted

        elif len(proposal_accepted_list) == 0:
            context.update({"no_join_requests": True})

        #for the chat room link on the student homepage, check if the user is an activity leader or member of any
        #activity
        activity_name = Organizations.objects.all().filter(leader1=request.user.username, approved=True)
        join_request_approved = JoinRequests.objects.all().filter(username=request.user.username, approved=True)

        #if the user is both a member and leader of some activities then when they click on the channel link
        #on student_home_page they will be directed to the group channel of the first activity they are a leader of
        if join_request_approved and activity_name:
            context.update({"activity_name":activity_name[0].org_name})

        #if the user is only the leader of some activities then when they click on the channel link on
        #student_home_page they will be directed to the group channel of the first activity they are a leader of
        elif activity_name:
            context.update({"activity_name":activity_name[0].org_name})

        #if the user is only the member of some activities then when they click on the channel link on
        #student_home_page they will be directed to the group channel of the first activity they are a member of
        elif join_request_approved:
            context.update({"member_channel":join_request_approved[0].org_name})

        join_request_denied = JoinRequests.objects.all().filter(username=request.user.username, rejected=True)
        join_request_nodecision = JoinRequests.objects.all().filter(username=request.user.username, approved=False, rejected=False)
        context.update({"join_request_approved":join_request_approved, "join_request_denied": join_request_denied, "join_request_nodecision": join_request_nodecision})

        return render(request, 'student_home_page.html', context)
    except:
        pass


    return render(request, 'student_home_page.html', context)



def applications(request,s):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.user.is_authenticated:
        user_identification = Accounts.objects.all().filter(email=request.user.email)
        if user_identification[0].student == True:
            return HttpResponseRedirect('/user/')

    context = {
        "action":request.POST.get('action'),
        "application_proposal": Organizations.objects.all().filter(id=s)[0],
    }


    if context["action"] == "accept":
        Organizations.objects.all().filter(id=s).update(approved=True)
        return HttpResponseRedirect('/user/')

    elif context["action"] == "reject":
        Organizations.objects.all().filter(id=s).update(rejected=True)
        return HttpResponseRedirect('/user/')



    return render(request, 'application_information.html', context)

def catalog(request):

    context = {
        "approved_list":Organizations.objects.all().filter(approved=True),
    }
    return render(request, 'catalog.html', context)

def activity_signup(request,s):

    activity_information = Organizations.objects.all().filter(id=s)[0]
    if activity_information.low:
        commitment = "Low"
    elif activity_information.medium:
        commitment = "Medium"
    elif activity_information.high:
        commitment = "High"


    members = JoinRequests.objects.all().filter(org_name=activity_information.org_name, approved=True)
    leaders = Organizations.objects.all().filter(org_name=activity_information.org_name, approved=True)[0]
    len_members = len(members)

    context = {
        "activity_information": activity_information,
        "commitment_level": commitment,
        "autenthicated": False,
        'action':request.POST.get('action'),
        'interest': request.POST.get('interest'),
        "not_many_proposals": True,
        "members": members,
        "leaders": leaders,
        "len_members": len_members,
        "cant_leave": None,

    }
    if activity_information.leader1 == request.user.username:
        context.update({"cant_leave":True})
    elif activity_information.leader1 != request.user.username:
        if len(JoinRequests.objects.all().filter(org_name = activity_information.org_name, username=request.user.username, approved=True)) > 0:
            context.update({"cant_leave":False})


    org_name = Organizations.objects.all().filter(id=s)[0].org_name
    if request.user.is_authenticated and (Accounts.objects.all().filter(email=request.user.email)[0].student == True):

        context.update({ "autenthicated": True})
        user_grade = Accounts.objects.all().filter(email=request.user.email)[0].grade
        num_activities_in = len(JoinRequests.objects.all().filter(username=request.user.username, approved=True))
        try:
            num_requests_sent = len(JoinRequests.objects.all().filter(org_name=org_name, username=request.user.username))
            if num_requests_sent >= 1:
                context.update({ "not_many_proposals": False, "no_more_requests": True})

        except:
            pass

        if context["action"] == "sub":
            JoinRequests.objects.create(org_name=org_name,first_name=request.user.first_name,
                last_name=request.user.last_name,username=request.user.username, grade=user_grade,
                interest_shown=(context["interest"]), num_activities_in=num_activities_in)
            return redirect("../../../student-page")


    return render(request, 'activity_signup.html', context)

def activity_leave(request, s):
    org_name = Organizations.objects.all().filter(id=s)[0].org_name
    obj = get_object_or_404(JoinRequests, org_name=org_name, username=request.user.username)
    obj.delete()
    return HttpResponseRedirect('/user/')


#excel sheet generation

def export_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="meetings.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Meetings')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Activity','Date', 'Description']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = Event.objects.all().values_list('activity','date', 'description')
    rows_2 = []
    for a in rows:
        rows_2.append(a)
    for row in rows_2:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


#meeting email reminder
events = Event.objects.all()
start_times = []
activity_names = []
for a in events:
    start_times.append(a.start_time)
    if a.activity not in activity_names:
        activity_names.append(a.activity)


#make time naive
start_times_naive = []
for time in start_times:
    start_times_naive.append(make_naive(time, timezone=None))

#6.5 hours before server time
from datetime import datetime
time_today = datetime.now()

#to match server time:
real_time_today = time_today - timedelta(hours=6.5)



def check_if_string_in_file(file_name, string_to_search):
    """ Check if any line in the file contains given string """
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            if string_to_search in line:
                return True
    return False



correct_meetings = []
for times in start_times_naive:
    if real_time_today >= (times - timedelta(hours=48)) and real_time_today <= times and not(check_if_string_in_file("meetings_email_sent.txt", str(times))):
        correct_meetings.append(times)
        file = open("meetings_email_sent.txt", "a")
        file.write(str(times) + '\n')
        file.close()


correct_activities_names = []
for activity in activity_names:
    for meeting in correct_meetings:
        if Event.objects.all().filter(start_time=make_aware(meeting, pytz.UTC))[0].activity == activity and activity not in correct_activities_names:
            correct_activities_names.append(activity)
emails = []


for activity in correct_activities_names:
    i = JoinRequests.objects.all().filter(org_name=activity, approved=True)
    for j in i:
        emails.append(User.objects.all().filter(username=j.username)[0].email)


if len(emails) != 0:
    import smtplib as sl
    server = sl.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.sendmail(settings.EMAIL_HOST_USER,emails,'You have an upcoming club meeting, please check your calendar to see which one.',)
