from datetime import datetime, timedelta
from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from .models import Leave, Holiday
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models import Q

def add_leave_with_calculation(user, leave_type, start_date_str, end_date_str, reason, fullName, empCode, username, uid):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()


    if end_date < start_date:
        return Response({
            "message": "End date cannot be before start date.",
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if there are any existing leave entries that overlap with the requested time period
    overlapping_leave = Leave.objects.filter(
        Q(user=user),
        Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date))
    )

    if overlapping_leave.exists():
        return Response({
            "message": "Leave request overlaps with an existing leave entry. Please check your leave schedule.",
        }, status=status.HTTP_400_BAD_REQUEST)

    requested_days = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:
            if not Holiday.objects.filter(date=current_date).exists():
                requested_days += 1
        current_date += timedelta(days=1)

    remaining_leave_days = getattr(user, f"{leave_type}_leave_days")

    if requested_days > remaining_leave_days:
        extra_days = requested_days - remaining_leave_days
        return Response({
            "message": f"Not enough leave days. You are requesting {extra_days} extra days. Please connect with HR.",
            "extra_days": extra_days
        }, status=status.HTTP_400_BAD_REQUEST)

    setattr(user, f"{leave_type}_leave_days", F(f"{leave_type}_leave_days") - requested_days)
    user.save()

    leaveCreation = Leave.objects.create(user=user, leave_type=leave_type, start_date=start_date, end_date=end_date, noOfDays = requested_days)


    context = {
            'full_name': fullName,
            'empcode': empCode,
            'username': username,
            'reason':reason
        }

    subject = f'Leave Request for {fullName}'
    
    html_message = render_to_string('take_leave.html', context)

    plain_message = strip_tags(html_message)

    email = "nihar@marolix.com"

    email_message = EmailMessage(
        subject,
        html_message,
        settings.EMAIL_HOST_USER,
        [email],
    )

    email_message.content_subtype = 'html'

    

    try:
        email_message.send(fail_silently=False)
        response_data = {
        "message": "Mail sent successfully",
        "id": uid    
        }
        status_code = status.HTTP_201_CREATED
    except Exception as e:
        response_data = {
            "message": "Some error occured",
            "id": uid
        }
        status_code = status.HTTP_408_REQUEST_TIMEOUT

 

    return JsonResponse({"message": "Leave added successfully",
                         "reason": reason,
                         "leave_id": leaveCreation.id}, status=status.HTTP_201_CREATED)