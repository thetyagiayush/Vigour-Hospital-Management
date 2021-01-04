import json
from datetime import datetime
from uuid import uuid4
import requests
from django.contrib import messages
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from vigour_app.models import Patients, LeaveReportDoctor, Doctors, FeedBackDoctors, CustomUser, PatientAppointment,NotificationPatient, NotificationDoctors


def doctor_home(request):
    doctor_obj=Doctors.objects.get(admin=request.user.id)
    appointment_doctor=PatientAppointment.objects.filter(leave_status="1",doctor_pref=request.user.username).count()
    total_appointment=PatientAppointment.objects.filter(doctor_pref=request.user.username).count()
    notification_count=NotificationDoctors.objects.filter(doctor_id=doctor_obj.id, read_status="0").count()
    doctor=Doctors.objects.get(admin=request.user.id)
    leave_count=LeaveReportDoctor.objects.filter(doctor_id=doctor.id,leave_status=1).count()
    return render(request,"doctor_template/doctor_home_template.html",{"notification_count":notification_count,"total_appointment":total_appointment,"appointment_doctor":appointment_doctor,"leave_count":leave_count})

def doctor_take_attendance(request):
    subjects=Subjects.objects.filter(doctor_id=request.user.id)
    session_years=SessionYearModel.object.all()
    return render(request,"doctor_template/doctor_take_attendance.html",{"subjects":subjects,"session_years":session_years})

@csrf_exempt
def get_patients(request):
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.object.get(id=session_year)
    patients=Patients.objects.filter(course_id=subject.course_id,session_year_id=session_model)
    list_data=[]

    for patient in patients:
        data_small={"id":patient.admin.id,"name":patient.admin.first_name+" "+patient.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

def doctor_apply_leave(request):
    doctor_obj = Doctors.objects.get(admin=request.user.id)
    leave_data=LeaveReportDoctor.objects.filter(doctor_id=doctor_obj)
    return render(request,"doctor_template/doctor_apply_leave.html",{"leave_data":leave_data})

def doctor_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("doctor_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        doctor_obj=Doctors.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportDoctor(doctor_id=doctor_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("doctor_apply_leave"))
        except:
            messages.error(request, "Failed To Apply for Leave")
            return HttpResponseRedirect(reverse("doctor_apply_leave"))

def doctor_appointment_view(request):
    leaves=PatientAppointment.objects.all()
    return render(request,"doctor_template/doctor_appointment_manage.html",{"leaves":leaves})

def doctor_appointment_approve(request,leave_id):
    leave=PatientAppointment.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("doctor_appointment_view"))

def doctor_appointment_disapprove(request,leave_id):
    leave=PatientAppointment.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("doctor_appointment_view"))

def doctor_feedback(request):
    doctor_id=Doctors.objects.get(admin=request.user.id)
    feedback_data=FeedBackDoctors.objects.filter(doctor_id=doctor_id)
    return render(request,"doctor_template/doctor_feedback.html",{"feedback_data":feedback_data})

def doctor_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("doctor_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        doctor_obj=Doctors.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackDoctors(doctor_id=doctor_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("doctor_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("doctor_feedback"))

def doctor_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    doctor=Doctors.objects.get(admin=user)
    return render(request,"doctor_template/doctor_profile.html",{"user":user,"doctor":doctor})

def doctor_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("doctor_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        address=request.POST.get("address")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            doctor=Doctors.objects.get(admin=customuser.id)
            doctor.address=address
            doctor.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("doctor_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("doctor_profile"))

@csrf_exempt
def doctor_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        doctor=Doctors.objects.get(admin=request.user.id)
        doctor.fcm_token=token
        doctor.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def doctor_all_notification(request):
    doctor=Doctors.objects.get(admin=request.user.id)
    notifications=NotificationDoctors.objects.filter(doctor_id=doctor.id)
    return render(request,"doctor_template/all_notification.html",{"notifications":notifications})

def doctor_send_notification(request):
    patients=Patients.objects.all()
    mypatients=PatientAppointment.objects.filter(doctor_pref=request.user.username)
    return render(request,"doctor_template/doctor_notification.html",{"patients":patients, "mypatients":mypatients})

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
    notification=Notificationpatient(patient_id=patient,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

def doctor_read_notification(request,notification_id):
    notification=NotificationDoctors.objects.get(id=notification_id)
    notification.read_status=1
    notification.save()
    return HttpResponseRedirect(reverse("doctor_all_notification"))
