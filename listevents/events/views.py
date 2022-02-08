import datetime
from curses.ascii import HT
from distutils.log import FATAL
from http.client import HTTPResponse
import imp
from locale import currency
from multiprocessing import context
from optparse import Values
from pickle import NONE
from pickletools import read_uint1
from re import template
import re
# from tkinter.messagebox import NO
from unicodedata import category
from urllib import response
from webbrowser import get
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView,UpdateView
from django.views.generic.list import ListView
from django.views.generic import RedirectView
from events import forms
from events.forms import UserRegisterForm,UserLoginForm,UserProfileUpdateForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from events.models import *
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .filters import EventFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
# stripe section
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
# mail section
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.generic.detail import DetailView

# dashoard section
class Dashboard(ListView):
            permission_classes = (AllowAny,)
            template_name = 'events/index.html'
            model = Event

            def get_context_data(self, **kwargs):
                category_list = []
                context = super().get_context_data(**kwargs)
                date =datetime.datetime.today().date()         
                event = Event.objects.filter(end_date__gte=date,published = 'True')     
                page = self.request.GET.get('page')
                paginator = Paginator(event,10)
                try:
                    pagin = paginator.page(page)
                except PageNotAnInteger:
                    pagin = paginator.page(1)
                except EmptyPage:
                    pagin = paginator.page(paginator.num_pages) 
                key = settings.STRIPE_PUBLISHABLE_KEY
                cate_qs = event.order_by().values('categories').distinct()                
                for i in cate_qs:
                    name = i['categories']
                    category_list.append(name)
                context = {
                   'event_object' : pagin,                   
                   'key':key,     
                   'category_list':category_list                        
                }            
                return context

# register section
class UserRegisterView(FormView):
           permission_classes = (AllowAny,)
           template_name = 'events/register.html'
           form_class = UserRegisterForm

           def form_valid(self, form):
                      self.obj = form.save(commit=False)
                      self.obj.password = make_password(self.obj.password)                      
                      self.obj.save()
                      return super().form_valid(form)

           def get_success_url(self):
                      return reverse_lazy('events:login')

# login section
class UserLoginView(FormView):
           permission_classes = [IsAuthenticated,]
           template_name = 'events/login.html' 
           form_class = UserLoginForm      

           def form_valid(self, form):                     
                      if self.request.user.is_authenticated:                                 
                                 return super(UserLoginView, self).form_valid(form)
                      else:                                
                                 username = form.cleaned_data['username']
                                 password = form.cleaned_data['password']
                                 user = authenticate(username=username, password=password)
                                 if user is not None and user.is_active:                                            
                                            login(self.request, user)
                                            return super(UserLoginView, self).form_valid(form)
                                 else:                                         
                                            return self.form_invalid(form)

           def get_success_url(self):                     
                      return reverse_lazy('events:user-profile')

# userprofile section  
class UserProfileView(TemplateView):
           permission_classes = [IsAuthenticated,]
           template_name = 'events/userprofile.html'

           def get_context_data(self, *args, **kwargs):  
                      event_list = []                                 
                      context = super(UserProfileView, self).get_context_data(*args, **kwargs)
                      date =datetime.datetime.today().date()    
                      userevnt_obj = UserEvent.objects.filter(user_id =self.request.user.id)                                  
                      user_detail = get_object_or_404(CustomUser, id=self.request.user.id)
                      for i in userevnt_obj:
                          title = i.event.title
                          desc = i.event.description
                          location = i.event.location
                          category = i.event.categories
                          startdate = i.event.start_date
                          event_list.append({
                              'title':title,'description':desc,'location':location,'category':category,'startdate':startdate
                          })                                       
                      context= {
                          'user_detail':user_detail,
                          'event_list' :event_list
                      }                     
                      return context


# logout section
class UserLogoutView(RedirectView):
    def get(self, request):       
        logout(request)
        return redirect('events:login')

# userprofile update section
class UserProfileUpdate(UpdateView): # code for update
    model = CustomUser
    form_class = UserProfileUpdateForm
    template_name = 'events/userprofileupdate.html'    

    def get_success_url(self):                    
                      return reverse_lazy('events:user-profile')
         
# userprofile image update section
class UserProfileImageUpdate(UpdateView):
    model = CustomUser
    fields=['image']
    template_name='events/profileimageupdate.html'

    def get_success_url(self):                     
                      return reverse_lazy('events:user-profile')



# payment using stripe and email notification section
def mail_sender(user,subject,message,email_from,recipient_list,event_obj): 
    to = recipient_list
    html_content = render_to_string('events/payment_email_notify.html',{'username':user.username,'email_from':email_from,'subject':subject,'message':message,'event_obj':event_obj})     
    from_email =settings.DEFAULT_FROM_EMAIL
    send_mail(subject,message, from_email,to,html_message= html_content)
    


class CreateCheckoutSessionView(View):
    def post(self,request,*args, **kwargs):
        user = self.request.user
        host = self.request.get_host()  
        event_id  = self.kwargs['pk']
        event_obj = Event.objects.get(id = event_id)  
        paid = event_obj.paid
        if paid == 'True':
            return HttpResponse("already paid")
        else:                    
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=[
                    'card',
                    ],
                line_items=[
                    {
                        'name': event_obj.title,
                        'quantity': 1,
                        'currency': 'inr',
                        'amount': 200000,
                    },
                    ],
                mode='payment',
            success_url = "http://{}{}".format(host,reverse('events:landing-page')),
            cancel_url = "http://{}{}".format(host,reverse('events:landing-page')),

        )
        event_obj.paid = 'True'
        event_obj.save()         
        user_event,created = UserEvent.objects.get_or_create(user_id = user.id ,event_id = event_obj.id)        
        user_event.save()
        subject = 'Successfull Booking of Event'
        message = f'Hi {user.username}, your payment is successfully completed and you booked the {event_obj.title}.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]             
        mail_sender(user,subject,message,email_from,recipient_list,event_obj)                                                                 
        return redirect(checkout_session.url, code=303)

 
# event search , filtering  amd pagination section
def is_valid_queryparam(param):
    return param != '' and param is not None


def filter(request):   
    date =datetime.datetime.today().date()            
    queryset = Event.objects.filter(end_date__gte=date,published = 'True')
    sdate_search = request.GET.get('sdate_search')
    edate_search = request.GET.get('edate_search')
    catey_search = request.GET.get('catey_search')
    query =request.POST.get('search',None)

    if is_valid_queryparam(sdate_search):
        qs = queryset.filter(start_date__icontains=sdate_search)
 
    if is_valid_queryparam(edate_search):
        qs = queryset.filter(end_date__icontains=edate_search)
        
    if is_valid_queryparam(catey_search) and catey_search != 'Select Category...':
        qs = queryset.filter(categories__icontains=catey_search)   

    if query:
            qs = queryset.filter(title__icontains = query).distinct()  
    page = request.GET.get('page')
    paginator = Paginator(qs, 10)
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)  
    return qs


def FilterSearchEvent(request):
    qs = filter(request)
    category_list = []
    date =datetime.datetime.today().date()         
    event = Event.objects.filter(end_date__gte=date,published = 'True') 
    cate_qs = event.order_by().values('categories').distinct()               
    for i in cate_qs:
        name = i['categories']
        category_list.append(name)
    context = {
        'queryset':qs,
        'category_list':category_list

    }
    return render(request,'events/index.html',context)



# likes and dislikes section
@login_required
def LikedEvent(request,id):
    user = request.user
    Like = False
    if request.method == "POST":
        event_id = request.POST['event_id']
        get_event = get_object_or_404(Event,id = event_id)
        if user in get_event.likes.all():
            get_event.likes.remove(user)
            Like = False
        else:
            if user in get_event.dislikes.all():
                get_event.dislikes.remove(user)
            get_event.likes.add(user)
            Like = True 
        data = {
            'liked':Like,
            'like_count':get_event.likes.all().count()
        }        
        return redirect(request.META['HTTP_REFERER']) # used to redirect to previous url.
    return redirect('events:landing-page')


@login_required
def DisLikedEvent(request, id):
    user=request.user
    Dislikes=False
    if request.method == "POST":
        event_id=request.POST['event_id']
        get_event = get_object_or_404(Event, id = event_id)
        if user in get_event.dislikes.all():
            get_event.dislikes.remove(user)
            Dislikes=False
        else:
            if user in get_event.likes.all():
                get_event.likes.remove(user)
         
            get_event.dislikes.add(user)
            get_event.save()
            Dislikes=True
        data={
            "disliked":Dislikes,
            'dislike_count':get_event.dislikes.all().count()
        }
        return redirect(request.META['HTTP_REFERER'])
    return redirect('events:landing-page')


# event details in read more

class EventDetailView(DetailView):
    model = Event

    def get_context_data(self, *args,**kwargs) :
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs['pk']
        event_details = get_object_or_404(Event,id=event_id)
        context={
            "eventid":event_id,
                'event_details':event_details
            }
        return context