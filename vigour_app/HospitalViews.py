from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from vigour_app.models import Hospital, CustomUser, FeedBackHospital,NotificationHospital

def hospital_home(request):
    hospi=Hospital.objects.get(admin=request.user.id)
    notifications=NotificationHospital.objects.filter(hospital_id=hospi.id, read_status="0").count()
    return render(request,"hospital_template/hospital_home_template.html",{"hospi":hospi, "noti":notifications})


def hospital_feedback(request):
    staff_id=Hospital.objects.get(admin=request.user.id)
    feedback_data=FeedBackHospital.objects.filter(hospital_id=staff_id)
    return render(request,"hospital_template/hospital_feedback.html",{"feedback_data":feedback_data})

def hospital_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("hospital_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        hospital_obj=Hospital.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackHospital(hospital_id=hospital_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("hospital_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("hospital_feedback"))

def hospital_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    hospital=Hospital.objects.get(admin=user)
    return render(request,"hospital_template/hospital_profile.html",{"user":user,"hospital":hospital})

def hospital_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("hospital_profile"))
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

            hospital=Hospital.objects.get(admin=customuser)
            hospital.address=address
            hospital.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("hospital_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("hospital_profile"))

def hospital_bed(request):
    hospi=Hospital.objects.get(admin=request.user.id)
    return render(request,"hospital_template/hospital_beds.html",{"hospi":hospi})

def hospital_bed_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("hospital_profile"))
    else:
        max_bed=request.POST.get("total_bed")
        available_bed=request.POST.get("available_bed")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            hospital=Hospital.objects.get(admin=customuser)
            hospital.max_bed=max_bed
            hospital.available_bed=available_bed
            hospital.updated_at = datetime.now()
            hospital.save()
            messages.success(request, "Successfully Updated Information")
            return HttpResponseRedirect(reverse("hospital_bed"))
        except:
            messages.error(request, "Failed to Update Information")
            return HttpResponseRedirect(reverse("hospital_bed"))


@csrf_exempt
def hospital_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        hospital=Hospital.objects.get(admin=request.user.id)
        hospital.fcm_token=token
        hospital.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def hospital_all_notification(request):
    hospital=Hospital.objects.get(admin=request.user.id)
    notifications=NotificationHospital.objects.filter(hospital_id=hospital.id)
    return render(request,"hospital_template/all_notification.html",{"notifications":notifications})

def hospital_read_notification(request,notification_id):
    notification=NotificationHospital.objects.get(id=notification_id)
    notification.read_status=1
    notification.save()
    return HttpResponseRedirect(reverse("hospital_all_notification"))