import secrets, string, re
from .models import *
from datetime import datetime
import pytz
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def generate_employee_code():
    latest_user = User.objects.order_by('-id').first()
    if not latest_user:
        newEmployeeCode = "MT-00001"
    else:
        latestAddedEmployee = latest_user.emplyeeIdentficationCode
        numeric_part = int(latestAddedEmployee.split('-')[1])
        new_numeric_part = numeric_part + 1
        newEmployeeCode = f"MT-{new_numeric_part:05d}"
        
    return newEmployeeCode

def get_current_time_and_date(timezone_str="Asia/Kolkata"):
    current_time_utc = datetime.now(pytz.utc)
    ist_timezone = pytz.timezone(timezone_str)
    current_time = current_time_utc.astimezone(ist_timezone)
    current_date = current_time.date()
    return current_time, current_date

def generate_random_string(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_username(name, designation):
    name = name.replace(" ", "").title()
    designation = designation.replace(" ", "")
    
    name = re.sub(r'[^a-zA-Z]', '', name)
    designation = re.sub(r'[^a-zA-Z]', '', designation)
    
    random_string = generate_random_string()
    
    username = f"{name}{designation}{random_string}"
    
    usernames = list(User.objects.values_list('username', flat=True))
    
    while username in usernames:
        random_string = generate_random_string()
        username = f"{name}{designation}{random_string}"
    
    return username

def send_email_payslipData(cases, success):
    subject = f'Payslip Generation {"Success" if success else "Failure"}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["nihar@marolix.com"]

    html_message = render_to_string('payslip_email_notification.html', {'cases': cases, 'success': success})

    try:
        email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
        email.attach_alternative(html_message, 'text/html')
        email.send()
    except Exception as e:
        return(f"Failed to send email notification: {e}")