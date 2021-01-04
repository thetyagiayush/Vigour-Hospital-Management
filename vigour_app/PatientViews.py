import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from vigour_app.models import Patients, CustomUser, \
    PatientAppointment, FeedBackPatient, NotificationPatient, Hospital, Doctors


def patient_home(request):
    
    patient_obj=Patients.objects.get(admin=request.user.id)
    total_appointment=PatientAppointment.objects.filter(patient_id=patient_obj.id).count()
    approved_appointment=PatientAppointment.objects.filter(patient_id=patient_obj.id,leave_status="1").count()
    notification_count=NotificationPatient.objects.filter(patient_id=patient_obj.id, read_status="0").count()
    return render(request,"patient_template/patient_home_template.html",{"notification_count":notification_count,"approved_appointment":approved_appointment,"total_appointment":total_appointment})


def patient_appointment(request):
    staff_obj = Patients.objects.get(admin=request.user.id)
    doctors=Doctors.objects.all()
    leave_data=PatientAppointment.objects.filter(patient_id=staff_obj)
    return render(request,"patient_template/patient_apply_appointment.html",{"leave_data":leave_data, "doctors":doctors})

def patient_appointment_history(request):
    staff_obj = Patients.objects.get(admin=request.user.id)
    leave_data=PatientAppointment.objects.filter(patient_id=staff_obj)
    return render(request,"patient_template/patient_view_appointment.html",{"leave_data":leave_data})

def patient_view_bed(request):
    hospitals=Hospital.objects.all()
    return render(request, "patient_template/patient_view_bed.html",{"hospitals":hospitals})

def patient_view_bed_click(request):
    hos_id=request.POST.get("hospital_id")
    hospital_obj=Hospital.objects.get(admin=hos_id)
    return render(request, "patient_template/patient_view_bed.html",{"hospi":hospital_obj})

def patient_appointment_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("patient_appointment"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")
        doctor_pref=request.POST.get("doctor_pref")
        patient_obj=Patients.objects.get(admin=request.user.id)
        try:
            leave_report=PatientAppointment(patient_id=patient_obj,leave_date=leave_date,doctor_pref=doctor_pref,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("patient_appointment"))
        except:
            messages.error(request, "Failed To Apply for Leave")
            return HttpResponseRedirect(reverse("patient_appointment"))


def patient_feedback(request):
    staff_id=Patients.objects.get(admin=request.user.id)
    feedback_data=FeedBackPatient.objects.filter(patient_id=staff_id)
    return render(request,"patient_template/patient_feedback.html",{"feedback_data":feedback_data})

def patient_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("patient_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        patient_obj=Patients.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackPatient(patient_id=patient_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("patient_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("patient_feedback"))

def patient_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    patient=Patients.objects.get(admin=user)
    return render(request,"patient_template/patient_profile.html",{"user":user,"patient":patient})

def patient_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("patient_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            patient=Patients.objects.get(admin=customuser)
            patient.address=address
            patient.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("patient_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("patient_profile"))

@csrf_exempt
def patient_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        patient=Students.objects.get(admin=request.user.id)
        patient.fcm_token=token
        patient.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def patient_all_notification(request):
    patient=Patients.objects.get(admin=request.user.id)
    notifications=NotificationPatient.objects.filter(patient_id=patient.id)
    return render(request,"patient_template/all_notification.html",{"notifications":notifications})

def patient_read_notification(request,notification_id):
    notification=NotificationPatient.objects.get(id=notification_id)
    notification.read_status=1
    notification.save()
    return HttpResponseRedirect(reverse("patient_all_notification"))