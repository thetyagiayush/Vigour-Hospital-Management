import json

import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from vigour_app.forms import AddPatientForm, EditPatientForm
from vigour_app.models import CustomUser, Doctors, Patients, \
    FeedBackPatient, FeedBackDoctors, PatientAppointment, LeaveReportDoctor, \
    NotificationPatient, NotificationDoctors, Hospital, NotificationHospital, FeedBackHospital


def admin_home(request):
    patient_count=Patients.objects.all().count()
    doctor_count=Doctors.objects.all().count()
    leave_count=LeaveReportDoctor.objects.filter(leave_status=0).count()
    appointment_count=PatientAppointment.objects.filter(leave_status=0).count()

    doctors=Doctors.objects.all()

    return render(request,"hod_template/home_content.html",{"appointment_count":appointment_count,"leave_count":leave_count,"patient_count":patient_count,"doctor_count":doctor_count})

def add_doctor(request):
    return render(request,"hod_template/add_doctor_template.html")

def add_doctor_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
            user.doctors.address=address
            user.save()
            messages.success(request,"Successfully Added Doctor")
            return HttpResponseRedirect(reverse("add_doctor"))
        except:
            messages.error(request,"Failed to Add Doctor")
            return HttpResponseRedirect(reverse("add_doctor"))

def add_patient(request):
    form=AddPatientForm()
    return render(request,"hod_template/add_patient_template.html",{"form":form})

def add_patient_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddPatientForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]
            sex=form.cleaned_data["sex"]
            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.patients.address=address
                user.patients.gender=sex
                user.save()
                messages.success(request,"Successfully Added Patient")
                return HttpResponseRedirect(reverse("add_patient"))
            except:
                messages.error(request,"Failed to Add Patient")
                return HttpResponseRedirect(reverse("add_patient"))
        else:
            form=AddPatientForm(request.POST)
            return render(request, "hod_template/add_patient_template.html", {"form": form})

def manage_doctor(request):
    doctors=Doctors.objects.all()
    return render(request,"hod_template/manage_doctor_template.html",{"doctors":doctors})

def manage_patient(request):
    patients=Patients.objects.all()
    return render(request,"hod_template/manage_patient_template.html",{"patients":patients})

def edit_doctor(request,doctor_id):
    doctor=Doctors.objects.get(admin=doctor_id)
    return render(request,"hod_template/edit_doctor_template.html",{"doctor":doctor,"id":doctor_id})

def edit_doctor_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        doctor_id=request.POST.get("doctor_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")

        try:
            user=CustomUser.objects.get(id=doctor_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()
            doctor_model=Doctors.objects.get(admin=doctor_id)
            doctor_model.address=address
            doctor_model.save()
            messages.success(request,"Successfully Edited doctor")
            return HttpResponseRedirect(reverse("edit_doctor",kwargs={"doctor_id":doctor_id}))
        except:
            messages.error(request,"Failed to Edit Doctor")
            return HttpResponseRedirect(reverse("edit_doctor",kwargs={"doctor_id":doctor_id}))

def edit_patient(request,patient_id):
    request.session['patient_id']=patient_id
    patient=Patients.objects.get(admin=patient_id)
    form=EditPatientForm()
    form.fields['email'].initial=patient.admin.email
    form.fields['first_name'].initial=patient.admin.first_name
    form.fields['last_name'].initial=patient.admin.last_name
    form.fields['username'].initial=patient.admin.username
    form.fields['address'].initial=patient.address
    form.fields['sex'].initial=patient.gender
    return render(request,"hod_template/edit_patient_template.html",{"form":form,"id":patient_id,"username":patient.admin.username})

def edit_patient_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        patient_id=request.session.get("patient_id")
        if patient_id==None:
            return HttpResponseRedirect(reverse("manage_patient"))

        form=EditPatientForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            sex = form.cleaned_data["sex"]
            try:
                user=CustomUser.objects.get(id=patient_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()
                patient=Patients.objects.get(admin=patient_id)
                patient.address=address
                patient.gender=sex
                patient.save()
                del request.session['patient_id']
                messages.success(request,"Successfully Edited Patient Details")
                return HttpResponseRedirect(reverse("edit_patient",kwargs={"patient_id":patient_id}))
            except:
                messages.error(request,"Failed to Edit Patient Details")
                return HttpResponseRedirect(reverse("edit_patient",kwargs={"patient_id":patient_id}))
        else:
            form=EditPatientForm(request.POST)
            patient=Patients.objects.get(admin=patient_id)
            return render(request,"hod_template/edit_patient_template.html",{"form":form,"id":patient_id,"username":patient.admin.username})

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def manage_all_notifications(request):
    return render(request, "hod_template/manage_all_notifications.html")

def manage_all_feedback(request):
    return render(request, "hod_template/manage_all_feedback.html")

def doctor_feedback_message(request):
    feedbacks=FeedBackDoctors.objects.all()
    return render(request,"hod_template/doctor_feedback_template.html",{"feedbacks":feedbacks})

def patient_feedback_message(request):
    feedbacks=FeedBackPatient.objects.all()
    return render(request,"hod_template/patient_feedback_template.html",{"feedbacks":feedbacks})

def hospital_feedback_message(request):
    feedbacks=FeedBackHospital.objects.all()
    return render(request,"hod_template/hospital_feedback_template.html",{"feedbacks":feedbacks})

@csrf_exempt
def hospital_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackHospital.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def patient_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackPatient.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def doctor_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackDoctors.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def doctor_leave_view(request):
    leaves=LeaveReportDoctor.objects.all()
    return render(request,"hod_template/doctor_leave_view.html",{"leaves":leaves})

def patient_appointment_view(request):
    leaves=PatientAppointment.objects.all()
    return render(request,"hod_template/patient_appointment_view.html",{"leaves":leaves})

def patient_approve_appointment(request,leave_id):
    leave=PatientAppointment.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("patient_appointment_view"))

def patient_disapprove_appointment(request,leave_id):
    leave=PatientAppointment.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("patient_appointment_view"))


def doctor_approve_leave(request,leave_id):
    leave=LeaveReportDoctor.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("doctor_leave_view"))

def doctor_disapprove_leave(request,leave_id):
    leave=LeaveReportDoctor.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("doctor_leave_view"))

def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"hod_template/admin_profile.html",{"user":user})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))

def admin_send_notification_patient(request):
    patients=Patients.objects.all()
    return render(request,"hod_template/patient_notification.html",{"patients":patients})

def admin_send_notification_doctor(request):
    doctors=Doctors.objects.all()
    return render(request,"hod_template/doctor_notification.html",{"doctors":doctors})

def admin_send_notification_hospital(request):
    hospital=Hospital.objects.all()
    return render(request,"hod_template/hospital_notification.html",{"hospital":hospital})

@csrf_exempt
def send_patient_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    patient=Patients.objects.get(admin=id)
    token=patient.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Vigour",
            "body":message,
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationPatient(patient_id=patient,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_doctor_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    doctor=Doctors.objects.get(admin=id)
    token=doctor.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Vigour",
            "body":message,
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationDoctors(doctor_id=doctor,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")


@csrf_exempt
def send_hospital_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    hospital=Hospital.objects.get(admin=id)
    token=hospital.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Vigour",
            "body":message,
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationHospital(hospital_id=hospital,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")
