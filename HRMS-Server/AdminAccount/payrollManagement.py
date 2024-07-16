from .views import *
from .models import User
import datetime
import json
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import pdfkit
from .s3Util import upload_to_s3
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

def generatePayslip(user):
    salary = user.salary
    salaryBreakUp = salaryBreakUpCalculation(user, salary)
    return JsonResponse({
        "message": "Salary Slip Generated",
        "data":(json.loads(salaryBreakUp.content))['data']
    })

def salaryBreakUpCalculation(user, salary):
    salary = int(salary)

    basicSalary = (salary * user.basic_salary) / 100
    hra = (salary * user.hra) / 100
    pf = (salary * user.pf) / 100
    specialAlllowance = (salary * user.special_allowances) / 100
    joiningDate = user.joining_date
    employeeId = user.emplyeeIdentficationCode

    totalSalary = basicSalary + hra + pf + specialAlllowance
    designation = user.designation

    dateOfPayslip_Generation = str(datetime.datetime.now())
    onlyDate = dateOfPayslip_Generation[:10]

    context = {
        "basicSalary": basicSalary,
        "hra": hra,
        "pf": pf,
        "specialAlllowance": specialAlllowance,
        "joiningDate": joiningDate,
        "employeeId": employeeId,
        "totalSalary": totalSalary,
        "designation": designation,
        "dateOfPayslipGeneration": onlyDate,
        "employeeName": user.first_name + " " + user.last_name
    }

    html_message = render_to_string(('salary_slip.html'), context)

    pdf_filename = f"{user.first_name} {user.last_name}_{employeeId}_{onlyDate}_salarySlip.pdf"
    pdfkit.from_string(html_message,pdf_filename)

    # Upload the PDF to S3
    s3_bucket = settings.BUCKET_NAME
    s3_file_path = f"{pdf_filename}"

    if upload_to_s3(pdf_filename, s3_bucket, s3_file_path):
        s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_file_path}"

        context = {
            'full_name': user.first_name + " " + user.last_name,
            'empcode': employeeId,
            'dateOfPayslipGeneration': onlyDate,
            'download_Payslip': s3_url
        }

        subject = f'Payslip Generated for {onlyDate}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        # HTML email content
        html_message = render_to_string('send_payslip_to_Employee.html', context)

        try:
            email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
            email.attach_alternative(html_message, 'text/html')
            email.send()
            return JsonResponse({"message": "Mail sent successfully", "data":s3_url}, status=status.HTTP_200_OK)
        except Exception as ex:
            return JsonResponse({"message": str(ex)}, status=status.HTTP_408_REQUEST_TIMEOUT)
    else:
        return JsonResponse({"message": "Some error occurred while uploading to S3"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)