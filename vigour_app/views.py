import datetime
import json
import os

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from vigour_app.EmailBackEnd import EmailBackEnd
from vigour_app.models import CustomUser
from vigour_system import settings


def showHome(request):
    return render(request,"index.html")

def contact(request):
    return render(request, "contactus.html")

def about(request):
    return render(request, "aboutus.html")

def ShowLoginPage(request):
    return render(request,"login_page.html")

def doLogin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
      
        user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user!=None:
            login(request,user)
            if user.user_type=="1":
                return HttpResponseRedirect('/admin_home')
            elif user.user_type=="2":
                return HttpResponseRedirect(reverse("doctor_home"))
            elif user.user_type=="3":
                return render(request,"index.html")
            else:
                return HttpResponseRedirect(reverse("hospital_home"))
        else:
            messages.error(request,"Invalid Login Details")
            return HttpResponseRedirect("/login")


def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def signup_admin(request):
    return render(request,"signup_admin_page.html")

def signup_patient(request):
    return render(request,"signup_patient_page.html")

def signup_doctor(request):
    return render(request,"signup_doctor_page.html")

def signup_hospital(request):
    return render(request,"signup_hospital_page.html")

def do_admin_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=1)
        user.save()
        messages.success(request,"Successfully Created Admin")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Admin")
        return HttpResponseRedirect(reverse("show_login"))

def do_doctor_signup(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")
    address=request.POST.get("address")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email, last_name=last_name,first_name=first_name,user_type=2)
        user.doctors.address=address
        user.save()
        messages.success(request,"Successfully Created Doctor")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email Already Registered')
            return HttpResponseRedirect('/signup_doctor')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username Already Registered!')
            return HttpResponseRedirect('/signup_doctor')
        else:
            messages.error(request,"Failed to Create Doctor")
            return HttpResponseRedirect(reverse("show_login"))

def do_hospital_signup(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")
    address=request.POST.get("address")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email, last_name=last_name,first_name=first_name,user_type=4)
        user.hospital.address=address
        user.save()
        messages.success(request,"Successfully Created Hospital Login")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email Already Registered')
            return HttpResponseRedirect('/signup_hospital')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username Already Registered!')
            return HttpResponseRedirect('/signup_hospital')
        else:
            messages.error(request,"Failed to Create Hospital Login")
            return HttpResponseRedirect(reverse("show_login"))

def do_signup_patient(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    address = request.POST.get("address")
    
    sex = request.POST.get("sex")

    try:
        user = CustomUser.objects.create_user(username=username, password=password, email=email, last_name=last_name,first_name=first_name, user_type=3)
        user.patients.address = address
        user.patients.gender = sex
        user.save()
        messages.success(request, "Successfully Added patient")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email Already Registered')
            return HttpResponseRedirect('/signup_patient')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username Already Registered!')
            return HttpResponseRedirect('/signup_patient')
        else:
            messages.error(request, "Failed to Add patient")
            return HttpResponseRedirect(reverse("signup_patient"))