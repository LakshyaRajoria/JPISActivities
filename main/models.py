from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
# Create your models here.

class Accounts(models.Model):
    f_name= models.CharField(default='First Name', max_length=120)
    l_name = models.CharField(max_length=120)
    email= models.EmailField()
    grade = models.TextField(null=True)
    student = models.BooleanField(default=False)
    administrator = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.email)



class Organizations(models.Model):
    org_name= models.CharField(max_length=120)
    email= models.EmailField() #this would be the email of the orgaization or their personal email they are using for contact with memebers
    tag1= models.CharField(max_length=120)
    tag2= models.CharField(null=True, max_length=120)
    tag3= models.CharField(null=True, max_length=120)
    advisor_name = models.CharField(max_length=120)
    low = models.BooleanField(default=False)
    medium = models.BooleanField(default=False)
    high = models.BooleanField(default=False)
    num_times = models.CharField(max_length=120) #num of times club meets in one week
    leader1= models.CharField(max_length=120) #name of the person making the club
    leader2= models.CharField(null=True, max_length=120)
    leader3= models.CharField(null=True,max_length=120)
    leader4= models.CharField(null=True, max_length=120)
    mission_statement = models.CharField(max_length=120)
    description = models.TextField()
    protocols = models.TextField()
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)


#for those trying to join club
class JoinRequests(models.Model):
  org_name= models.CharField(max_length=120)
  first_name = models.CharField(max_length=120)
  last_name = models.CharField(max_length=120)
  username = models.CharField(default='username1', max_length=120)
  grade = models.CharField(max_length=120)
  interest_shown = models.CharField(null=True, max_length=120)
  num_activities_in = models.CharField(max_length=120)
  approved = models.BooleanField(default=False)
  rejected = models.BooleanField(default=False)

#fpr messaging platform
User = get_user_model()

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField()
    room_name = models.TextField()

    def __str__(self):
        return self.author.username

    def last_10_messages():
        return Message.objects.order_by('-timestamp').all()[:10]
