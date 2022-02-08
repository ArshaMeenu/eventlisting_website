from distutils.command.upload import upload
import email
from operator import truediv
from pyexpat import model
from django.db import models  
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone  
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from django_countries.fields import CountryField

# custom user
  
class CustomUser(AbstractUser): 
    image = models.ImageField(upload_to='events/media',null = True,blank =True)
    username = models.CharField(max_length=100,blank=True,null=True)
    first_name = models.CharField(max_length=100,blank=True,null=True)
    last_name = models.CharField(max_length=100,blank=True,null=True)
    email = models.EmailField(unique=True)

  
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []  


# event model

class Event(models.Model):
    Categories_Choices = (
        ('Under-Graduate','Under-Graduate'),
        ('Post-Graduate','Post-Graduate'),
        ('Doctoralstudies','Doctoralstudies'),
        ('Vocational Education','Vocational Education'),
        ('Distance Education','Distance Education')
      )
    title =models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    location = CountryField(blank=True)    
    start_date = models.DateField(blank=True, null=True)
    end_date= models.DateField(blank=True, null=True)
    event_image = models.ImageField(upload_to = 'events/images',null = True,blank =True)
    categories = models.CharField(max_length=100,choices=Categories_Choices, default="UG")
    published = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    likes = models.ManyToManyField(CustomUser,blank =True,related_name='event_likes')
    dislikes=models.ManyToManyField(CustomUser,blank =True,related_name="event_disliked")
    price = models.IntegerField(default=0)
 
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['start_date']


    def num_likes(self):
        return self.likes.count()

    def num_dislikes(self):
        return self.dislikes.count()

# user-event model

class UserEvent(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='user_event')
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    
# Like section

LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)
class Like(models.Model): 
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, max_length=8)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}-{self.event}-{self.value}"

    