from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from django.http import JsonResponse
from .serializers import RegisterSerializer
from .models import *
from .views import *
from .models import User


def add_employee(body):
    serializer = RegisterSerializer(data=body)
    if serializer.is_valid():
        serializer.save()

        # assigning User the Reporting Manager
        userIdOfNewUser = User.objects.get(username = serializer.data['username'])
        reportingManagerId = User.objects.get(id = body['ReportingManager'])

        savinfToReportingManagerAssignment = ReportingManagerAssignment.objects.create(user =userIdOfNewUser,reporting_manager = reportingManagerId )

        username = serializer.data['username']
        user = User.objects.get(username=username)
        empid = user.emplyeeIdentficationCode
        email = user.email
        reportingManager = User.objects.get(id = body['ReportingManager']).first_name+" "+User.objects.get(id = body['ReportingManager']).last_name

        context = {
                'full_name': serializer.data['first_name']+ " "+serializer.data['last_name'],
                'empcode': empid,
                'username': username,
                'password': body['password'],
                'reportingManager':reportingManager
            }

        subject = 'Congratulations'
        
        html_message = render_to_string('email_template_employee.html', context)

        plain_message = strip_tags(html_message)

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
            "data": serializer.data,
            "id": user.id    
            }
            status_code = status.HTTP_201_CREATED
        except Exception as e:
            response_data = {
                "message": "Some error occured",
                "data": serializer.data,
                "id": user.id
            }
            status_code = status.HTTP_408_REQUEST_TIMEOUT

        return Response({
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_200_OK)