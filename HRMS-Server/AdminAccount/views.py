from rest_framework import generics,status,views,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer
from .leaveManagement import add_leave_with_calculation
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.core.cache import cache
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from .models import *
import json
import string
import secrets
from .holiday_management import add_holidayy
from .password_reset_file import reset_password
from .add_employee_view import add_employee
from django.db import IntegrityError
from .utils import *
from .payrollManagement import generatePayslip
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction


# Create your views here.

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def post(self,request):
        user=request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        username = serializer.validated_data['username']
        userId = User.objects.get(username = username).id
        empcode = User.objects.get(username = username).emplyeeIdentficationCode
        email = serializer.validated_data['email']
        context = {
            'full_name': serializer.validated_data['first_name']+ " "+serializer.validated_data['last_name'],
            'empcode': empcode,
            'username': username,
            'password': serializer.validated_data['password'],
        }

        subject = 'Congratulations'
        
        html_message = render_to_string('email_template.html', context)

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
            "data": user_data,
            "id": userId    
            }
            status_code = status.HTTP_201_CREATED
        except Exception as e:
            response_data = {
                "message": "Some error occured",
                "data": user_data,
                "id": userId
            }
            status_code = status.HTTP_408_REQUEST_TIMEOUT

        return JsonResponse(response_data, status=status_code)
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        userId = User.objects.get(username = username).id
        isAdmin = User.objects.get(username=username).isAdmin
        userAccessData = {
                "isAdmin":isAdmin,
                "can_read_holidays":User.objects.get(username=username).can_read_holidays,
                "can_write_holidays":User.objects.get(username=username).can_write_holidays,
                "can_create_holidays":User.objects.get(username=username).can_create_holidays,
                "can_delete_holidays":User.objects.get(username=username).can_delete_holidays,
                "can_import_holidays":User.objects.get(username=username).can_import_holidays,
                "can_export_holidays":User.objects.get(username=username).can_export_holidays,

                "can_read_leaves":User.objects.get(username=username).can_read_leaves,
                "can_write_leaves":User.objects.get(username=username).can_write_leaves,
                "can_create_leaves":User.objects.get(username=username).can_create_leaves,
                "can_delete_leaves":User.objects.get(username=username).can_delete_leaves,
                "can_import_leaves":User.objects.get(username=username).can_import_leaves,
                "can_export_leaves":User.objects.get(username=username).can_export_leaves,

                "can_read_clients":User.objects.get(username=username).can_read_clients,
                "can_write_clients":User.objects.get(username=username).can_write_clients,
                "can_create_clients":User.objects.get(username=username).can_create_clients,
                "can_delete_clients":User.objects.get(username=username).can_delete_clients,
                "can_import_clients":User.objects.get(username=username).can_import_clients,
                "can_export_clients":User.objects.get(username=username).can_export_clients,
                "can_add_employees":User.objects.get(username=username).can_add_employees,
                "can_remove_employees":User.objects.get(username=username).can_remove_employees,
                "can_update_employees":User.objects.get(username=username).can_update_employees,

                "can_read_projects":User.objects.get(username=username).can_read_projects,
                "can_write_projects":User.objects.get(username=username).can_write_projects,
                "can_create_projects":User.objects.get(username=username).can_create_projects,
                "can_delete_projects":User.objects.get(username=username).can_delete_projects,
                "can_import_projects":User.objects.get(username=username).can_import_projects,
                "can_export_projects":User.objects.get(username=username).can_export_projects,

                "can_read_tasks":User.objects.get(username=username).can_read_tasks,
                "can_write_tasks":User.objects.get(username=username).can_write_tasks,
                "can_create_tasks":User.objects.get(username=username).can_create_tasks,
                "can_delete_tasks":User.objects.get(username=username).can_delete_tasks,
                "can_import_tasks":User.objects.get(username=username).can_import_tasks,
                "can_export_tasks":User.objects.get(username=username).can_export_tasks,

                "can_read_chats":User.objects.get(username=username).can_read_chats,
                "can_write_chats":User.objects.get(username=username).can_write_chats,
                "can_create_chats":User.objects.get(username=username).can_create_chats,
                "can_delete_chats":User.objects.get(username=username).can_delete_chats,
                "can_import_chats":User.objects.get(username=username).can_import_chats,
                "can_export_chats":User.objects.get(username=username).can_export_chats,

                "can_read_assets":User.objects.get(username=username).can_read_assets,
                "can_write_assets":User.objects.get(username=username).can_write_assets,
                # "can_create_assets":User.objects.get(username=username).can_create_assets,
                "can_delete_assets":User.objects.get(username=username).can_delete_assets,
                "can_import_assets":User.objects.get(username=username).can_import_assets,
                "can_export_assets":User.objects.get(username=username).can_export_assets,

                "can_read_timing_sheets":User.objects.get(username=username).can_read_timing_sheets,
                "can_write_timing_sheets":User.objects.get(username=username).can_write_timing_sheets,
                "can_create_timing_sheets":User.objects.get(username=username).can_create_timing_sheets,
                "can_delete_timing_sheets":User.objects.get(username=username).can_delete_timing_sheets,
                "can_import_timing_sheets":User.objects.get(username=username).can_import_timing_sheets,
                "can_export_timing_sheets":User.objects.get(username=username).can_export_timing_sheets
                }
        return JsonResponse({
            "message":"User logged in successfully",
            
            
            "id":userId,
            "data":serializer.data,
            "userAccessData":[userAccessData]
        },
        status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['POST'])
def send_otp(request):
    email = (json.loads(request.body))['email']
    from .send_otp_logic import sendOtp
    resp = sendOtp(email)
    return JsonResponse({"message": "OTP sent successfully", 
                         "status":resp.status_code}, 
                        status=status.HTTP_200_OK)

@api_view(['POST'])
def confirm_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    cached_otp = cache.get(email)
    if cached_otp is None or cached_otp != otp:
        return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    result = reset_password(email, password, confirm_password)  
    return result 

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_employee_view(request):
    if request.method == 'POST' and request.user.isAdmin == True or request.user.can_add_employees == True:
        body = json.loads(request.body)

        reportingManager = (User.objects.get(username = body['ReportingManager'])).id
        body['ReportingManager'] = reportingManager

        characters = string.ascii_letters + string.digits + string.punctuation
        password_length = 8
        password = ''.join(secrets.choice(characters) for _ in range(password_length))
        body['password'] = password
        fullName = body['first_name'] +" " +body['last_name']
        designation = body['designation']
        username = generate_username(fullName, designation)
        body['username'] = username
        resp = add_employee(body)
        
        return resp
    else:
        return JsonResponse({
            "status": "failed",
            "message": "User not authorized"
        },
        status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def addDesignation(request):
    designation_name = (json.loads(request.body))['des']

    try:
        objDesignation = Designation.objects.create(name=designation_name)

        return JsonResponse(
            {
                "status": "Success",
                "designationId":objDesignation.id,
                "message": f"Designation '{designation_name}' added successfully"
            }, status=status.HTTP_201_CREATED
        )

    except IntegrityError:
        return JsonResponse(
            {
                "status": "Error",
                "message": f"Designation '{designation_name}' already exists"
            }, status=status.HTTP_400_BAD_REQUEST
        )
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def addDepartment(request):
    department_name = (json.loads(request.body))['dep']

    try:
        objDepartment = Department.objects.create(name=department_name)

        return JsonResponse(
            {
                "status": "Success",
                "departmentId":objDepartment.id,
                "message": f"Department '{department_name}' added successfully"
            }, status=status.HTTP_201_CREATED
        )

    except IntegrityError:
        return JsonResponse(
            {
                "status": "Error",
                "message": f"Department '{department_name}' already exists"
            }, status=status.HTTP_400_BAD_REQUEST
        )
    
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def getAllDesignations(request):
    designations = Designation.objects.all()
    data = [{'id': des.id, 'name': des.name} for des in designations]
    return JsonResponse({'designations': data}, safe=False, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def getAllDepartments(request):
    departments = Department.objects.all()
    data = [{'id': dep.id, 'name': dep.name} for dep in departments]
    return JsonResponse({'departments': data}, safe=False, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def updateDesignation(request):
    try:
        designation_id = (json.loads(request.body))['designationId']
        designation = Designation.objects.get(id=designation_id)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"status": "Error", "message": "Designation not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    new_name = (json.loads(request.body))['new_name']
    designation.name = new_name
    designation.save()

    return JsonResponse(
        {"status": "Success", "message": f"Designation updated to '{new_name}'"},
        status=status.HTTP_200_OK
    )

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def updateDepartment(request):
    try:
        department_id = (json.loads(request.body))['departmentId']
        department = Department.objects.get(id=department_id)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"status": "Error", "message": "Department not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    new_name = (json.loads(request.body))['new_name']
    department.name = new_name
    department.save()

    return JsonResponse(
        {"status": "Success", "message": f"department updated to '{new_name}'"},
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def deleteDesignation(request):
    try:
        designation_id  = (json.loads(request.body))['designationId']
        designation = Designation.objects.get(id=designation_id)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"status": "Error", "message": "Designation not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    designation.delete()

    return JsonResponse(
        {"status": "Success", "message": "Designation deleted"},
        status=status.HTTP_204_NO_CONTENT
    )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def deleteDepartment(request):
    try:
        department_id  = (json.loads(request.body))['departmentId']
        department = Department.objects.get(id=department_id)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"status": "Error", "message": "Department not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    department.delete()

    return JsonResponse(
        {"status": "Success", "message": "Department deleted"},
        status=status.HTTP_204_NO_CONTENT
    )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def getAllEmployees(request):
    user_fields = User.objects.filter(is_active=True, isOwner=False).annotate(full_name=Concat('first_name', Value(' '), 'last_name')).order_by('id').values(
    "id",
    "email",
    "first_name",
    "last_name",
    "username",
    "emplyeeIdentficationCode",
    "joining_date",
    "phone",
    "isAdmin",
    "designation",
    "casual_leave_days",
    "salary",
    "currency",
    "medical_leave_days",
    "lop_leave_days",
    "department",
    "isReportingManager",
    "reporting_manager",
    "can_add_employees",
    "can_remove_employees",
    "can_update_employees",
    "can_read_holidays",
    "can_write_holidays",
    "can_create_holidays",
    "can_delete_holidays",
    "can_import_holidays",
    "can_export_holidays",
    "can_read_leaves",
    "can_write_leaves",
    "can_create_leaves",
    "can_delete_leaves",
    "can_import_leaves",
    "can_export_leaves",
    "can_read_clients",
    "can_write_clients",
    "can_create_clients",
    "can_delete_clients",
    "can_import_clients",
    "can_export_clients",
    "can_read_projects",
    "can_write_projects",
    "can_create_projects",
    "can_delete_projects",
    "can_import_projects",
    "can_export_projects",
    "can_read_tasks",
    "can_write_tasks",
    "can_create_tasks",
    "can_delete_tasks",
    "can_import_tasks",
    "can_export_tasks",
    "can_read_chats",
    "can_write_chats",
    "can_create_chats",
    "can_delete_chats",
    "can_import_chats",
    "can_export_chats",
    "can_read_assets",
    "can_create_assets",
    "can_write_assets",
    "can_delete_assets",
    "can_import_assets",
    "can_export_assets",
    "can_read_timing_sheets",
    "can_write_timing_sheets",
    "can_create_timing_sheets",
    "can_delete_timing_sheets",
    "can_import_timing_sheets",
    "can_export_timing_sheets",
    'isOwner'
)

    user_data = [
        {
            'id': user['id'],
            "email": user['email'],
            "first_name": user['first_name'],
            "username": user['username'],
            "designation": user['designation'],
            "last_name": user['last_name'],
            "emplyeeIdentficationCode": user['emplyeeIdentficationCode'],
            "joining_date": user['joining_date'],
            "phone": user['phone'],
            "isAdmin": user['isAdmin'],
            "casual_leave_days": user['casual_leave_days'],
            "salary": user['salary'],
            "currency": user['currency'],
            "medical_leave_days": user['medical_leave_days'],
            "lop_leave_days": user['lop_leave_days'],
            "department": user['department'],
            "isReportingManager":user['isReportingManager'],
            "ReportingManager":' '.join(User.objects.filter(reporting_manager=user['reporting_manager']).values_list('first_name', flat=True)),
            "can_add_employees": user['can_add_employees'],
            "can_remove_employees": user['can_remove_employees'],
            "can_update_employees": user['can_update_employees'],
            "can_read_holidays": user['can_read_holidays'],
            "can_write_holidays": user['can_write_holidays'],
            "can_create_holidays": user['can_create_holidays'],
            "can_delete_holidays": user['can_delete_holidays'],
            "can_import_holidays": user['can_import_holidays'],
            "can_export_holidays": user['can_export_holidays'],
            "can_read_leaves": user['can_read_leaves'],
            "can_write_leaves": user['can_write_leaves'],
            "can_create_leaves": user['can_create_leaves'],
            "can_delete_leaves": user['can_delete_leaves'],
            "can_import_leaves": user['can_import_leaves'],
            "can_export_leaves": user['can_export_leaves'],
            "can_read_clients": user['can_read_clients'],
            "can_write_clients": user['can_write_clients'],
            "can_create_clients": user['can_create_clients'],
            "can_delete_clients": user['can_delete_clients'],
            "can_import_clients": user['can_import_clients'],
            "can_export_clients": user['can_export_clients'],
            "can_read_projects": user['can_read_projects'],
            "can_write_projects": user['can_write_projects'],
            "can_create_projects": user['can_create_projects'],
            "can_delete_projects": user['can_delete_projects'],
            "can_import_projects": user['can_import_projects'],
            "can_export_projects": user['can_export_projects'],
            "can_read_tasks": user['can_read_tasks'],
            "can_write_tasks": user['can_write_tasks'],
            "can_create_tasks": user['can_create_tasks'],
            "can_delete_tasks": user['can_delete_tasks'],
            "can_import_tasks": user['can_import_tasks'],
            "can_export_tasks": user['can_export_tasks'],
            "can_read_chats": user['can_read_chats'],
            "can_write_chats": user['can_write_chats'],
            "can_create_chats": user['can_create_chats'],
            "can_delete_chats": user['can_delete_chats'],
            "can_import_chats": user['can_import_chats'],
            "can_export_chats": user['can_export_chats'],
            "can_read_assets": user['can_read_assets'],
            "can_create_assets": user['can_create_assets'],
            "can_write_assets": user['can_write_assets'],
            "can_delete_assets": user['can_delete_assets'],
            "can_import_assets": user['can_import_assets'],
            "can_export_assets": user['can_export_assets'],
            "can_read_timing_sheets": user['can_read_timing_sheets'],
            "can_write_timing_sheets": user['can_write_timing_sheets'],
            "can_create_timing_sheets": user['can_create_timing_sheets'],
            "can_delete_timing_sheets": user['can_delete_timing_sheets'],
            "can_import_timing_sheets": user['can_import_timing_sheets'],
            "can_export_timing_sheets": user['can_export_timing_sheets'],
            "isOwner":user['isOwner'],
        }
        for user in user_fields
    ]

    return JsonResponse({'data': user_data})

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user(request):
    try:
        if request.method == 'PUT':
            if request.user.isAdmin == True or request.user.can_add_employees == True:
                data = json.loads(request.body)
                if data['email']:
                    user = User.objects.get(email = data['email'])
                    userId = user.id
                    email = data['email']
                    username = data['username']
                    characters = string.ascii_letters + string.digits + string.punctuation
                    password_length = 8
                    password = ''.join(secrets.choice(characters) for _ in range(password_length))
                    confirmPassword = data['confirmPassword']
                    first_name = data['first_name']
                    last_name = data['last_name']
                    empId = data['emplyeeIdentficationCode']
                    joining_date =  data['joining_date']
                    phone = data['phone']
                    department = data['department']
                    designation = data['designation']
                    can_read_holidays = data['can_read_holidays']
                    can_write_holidays = data['can_write_holidays']
                    can_create_holidays = data['can_create_holidays']
                    can_delete_holidays = data['can_delete_holidays']
                    can_import_holidays = data['can_import_holidays']
                    can_export_holidays = data['can_export_holidays']
                    can_read_leaves = data['can_read_leaves']
                    can_write_leaves = data['can_write_leaves']
                    can_create_leaves = data['can_create_leaves']
                    can_delete_leaves = data['can_delete_leaves']
                    can_import_leaves = data['can_import_leaves']
                    can_export_leaves = data['can_export_leaves']
                    can_read_clients = data['can_read_clients']
                    can_write_clients = data['can_write_clients']
                    can_create_clients = data['can_create_clients']
                    can_delete_clients = data['can_delete_clients']
                    can_import_clients = data['can_import_clients']
                    can_export_clients = data['can_export_clients']
                    can_read_projects = data['can_read_projects']
                    can_write_projects = data['can_write_projects']
                    can_create_projects = data['can_create_projects']
                    can_delete_projects = data['can_delete_projects']
                    can_import_projects = data['can_import_projects']
                    can_export_projects = data['can_export_projects']
                    can_read_tasks = data['can_read_tasks']
                    can_write_tasks = data['can_write_tasks']
                    can_create_tasks = data['can_create_tasks']
                    can_delete_tasks = data['can_delete_tasks']
                    can_import_tasks = data['can_import_tasks']
                    can_export_tasks = data['can_export_tasks']
                    can_read_chats  =data['can_read_chats']
                    can_write_chats  =data['can_write_chats']
                    can_create_chats  =data['can_create_chats']
                    can_delete_chats  =data['can_delete_chats']
                    can_import_chats  =data['can_import_chats']
                    can_export_chats  =data['can_export_chats']
                    can_read_assets = data['can_read_assets']
                    can_write_assets = data['can_write_assets']
                    can_create_assets = data['can_create_assets']
                    can_delete_assets = data['can_delete_assets']
                    can_import_assets = data['can_import_assets']
                    can_export_assets = data['can_export_assets']
                    can_read_timing_sheets = data['can_read_timing_sheets']
                    can_write_timing_sheets = data['can_write_timing_sheets']
                    can_create_timing_sheets = data['can_create_timing_sheets']
                    can_delete_timing_sheets = data['can_delete_timing_sheets']
                    can_import_timing_sheets = data['can_import_timing_sheets']
                    can_export_timing_sheets = data['can_export_timing_sheets']
                    casual_leave_days = data['casual_leave_days']
                    medical_leave_days = data['medical_leave_days']
                    lop_leave_days = data['lop_leave_days']

                    if password != "" and password == confirmPassword:
                        user.set_password(password)
                        user.save()

                    user_data = User.objects.filter(id = userId).update(
                        email=email,
                        username = username if username else "",
                        first_name=first_name if first_name else "",
                        last_name=last_name if last_name else "",
                        emplyeeIdentficationCode=empId if empId else "",
                        joining_date=joining_date if joining_date else "",
                        phone=phone if phone else "",
                        casual_leave_days =casual_leave_days if casual_leave_days else"",
                        medical_leave_days =medical_leave_days if medical_leave_days else"",
                        lop_leave_days =lop_leave_days if lop_leave_days else"",
                        department=department if department else "",
                        designation=designation if designation else "",
                        can_read_holidays = can_read_holidays if can_read_holidays else "",
                        can_write_holidays = can_write_holidays if can_write_holidays else "",
                        can_create_holidays = can_create_holidays if can_create_holidays else "",
                        can_delete_holidays = can_delete_holidays if can_delete_holidays else "",
                        can_import_holidays = can_import_holidays if can_import_holidays else "",
                        can_export_holidays = can_export_holidays if can_export_holidays else "",

                        can_read_leaves = can_read_leaves if can_read_leaves else "",
                        can_write_leaves = can_write_leaves if can_write_leaves else "",
                        can_create_leaves = can_create_leaves if can_create_leaves else "",
                        can_delete_leaves = can_delete_leaves if can_delete_leaves else "",
                        can_import_leaves = can_import_leaves if can_import_leaves else "",
                        can_export_leaves = can_export_leaves if can_export_leaves else "",

                        can_read_clients = can_read_clients if can_read_clients else "",
                        can_write_clients = can_write_clients if can_write_clients else "",
                        can_create_clients = can_create_clients if can_create_clients else "",
                        can_delete_clients = can_delete_clients if can_delete_clients else "",
                        can_import_clients = can_import_clients if can_import_clients else "",
                        can_export_clients = can_export_clients if can_export_clients else "",

                        can_read_projects = can_read_projects if can_read_projects else "",
                        can_write_projects = can_write_projects if can_write_projects else "",
                        can_create_projects = can_create_projects if can_create_projects else "",
                        can_delete_projects = can_delete_projects if can_delete_projects else "",
                        can_import_projects = can_import_projects if can_import_projects else "",
                        can_export_projects = can_export_projects if can_export_projects else "",

                        can_read_tasks = can_read_tasks if can_read_tasks else "",
                        can_write_tasks = can_write_tasks if can_write_tasks else "",
                        can_create_tasks = can_create_tasks if can_create_tasks else "",
                        can_delete_tasks = can_delete_tasks if can_delete_tasks else "",
                        can_import_tasks = can_import_tasks if can_import_tasks else "",
                        can_export_tasks = can_export_tasks if can_export_tasks else "",

                        can_read_chats = can_read_chats if can_read_chats else "",
                        can_write_chats = can_write_chats if can_write_chats else "",
                        can_create_chats = can_create_chats if can_create_chats else "",
                        can_delete_chats = can_delete_chats if can_delete_chats else "",
                        can_import_chats = can_import_chats if can_import_chats else "",
                        can_export_chats = can_export_chats if can_export_chats else "",

                        can_read_assets = can_read_assets if can_read_assets else "",
                        can_write_assets = can_write_assets if can_write_assets else "",
                        can_create_assets = can_create_assets if can_create_assets else "",
                        can_delete_assets = can_delete_assets if can_delete_assets else "",
                        can_import_assets = can_import_assets if can_import_assets else "",
                        can_export_assets = can_export_assets if can_export_assets else "",

                        can_read_timing_sheets = can_read_timing_sheets if can_read_timing_sheets else "",
                        can_write_timing_sheets = can_write_timing_sheets if can_write_timing_sheets else "",
                        can_create_timing_sheets = can_create_timing_sheets if can_create_timing_sheets else "",
                        can_delete_timing_sheets = can_delete_timing_sheets if can_delete_timing_sheets else "",
                        can_import_timing_sheets = can_import_timing_sheets if can_import_timing_sheets else "",
                        can_export_timing_sheets = can_export_timing_sheets if can_export_timing_sheets else ""


                    )

                context = {
                    'full_name': first_name+ " "+last_name,
                    'empcode': empId,
                    'username': username,
                    'password': password,
                }

                subject = 'Password Changed'
                
                html_message = render_to_string('password_changed.html', context)

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
                    "data": user_data,
                    "id": user.id    
                    }
                    status_code = status.HTTP_201_CREATED
                except Exception as e:
                    response_data = {
                        "message": "Some error occured",
                        "data": user_data,
                        "id": user.id
                    }
                    status_code = status.HTTP_408_REQUEST_TIMEOUT

                return JsonResponse({
                    "message":"User updated successfully"
                },
                status = status.HTTP_200_OK)
            
        else:
            
            raise Exception("user not authorised")
            
            

    except Exception as ex:
        return JsonResponse({
            "message":str(ex)
        },
        status = status.HTTP_401_UNAUTHORIZED)

    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deactivate_user(request):
    try:
        if request.user.isAdmin == False or request.user.can_remove_employees == False:
            raise Exception("user not authorised")
        
        data = json.loads(request.body)
        user = User.objects.get(email=data['email'])

        if user.isOwner == True:
            return JsonResponse({
            "message": "You do not have access to remove this particular member",
            "status":"Failed"
        },
        status = status.HTTP_401_UNAUTHORIZED)

        else:
            user.is_active = False
            user.save()
            return JsonResponse({
                "message": f"User {user.username} with employee ID - {user.emplyeeIdentficationCode} deactivated from the employee list successfully",
                "status":"success"
            },
            status = status.HTTP_200_OK)

        
    except Exception as ex:
        return JsonResponse({
            "message": str(ex),
            "status":"failed"
        },
        status = status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request):
    userData=User.objects.filter(is_active=True).values('id','username', 'emplyeeIdentficationCode', 'designation')
    userList=list(userData)
    return JsonResponse(userList, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def get_particular_employee_data(request):
    userId=(json.loads(request.body))['id']

    user=User.objects.get(id=userId)

    if user.isOwner==True:
        full_name_of_reporting_manager="N/A"
    else:
        rep=ReportingManagerAssignment.objects.get(user=userId)
        firstname=rep.reporting_manager.first_name if rep.reporting_manager.first_name else ""
        lastname=rep.reporting_manager.last_name if rep.reporting_manager.last_name else ""
        full_name_of_reporting_manager=firstname+" "+ lastname



    userDetails={
        "id": userId,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "emplyeeIdentficationCode": user.emplyeeIdentficationCode,
        "joining_date": user.joining_date,
        "phone": user.phone,
        "isAdmin": user.isAdmin,
        "isOwner": user.isOwner,
        "casual_leave_days": user.casual_leave_days,
        "salary": user.salary,
        "currency": user.currency,
        "medical_leave_days": user.medical_leave_days,
        "lop_leave_days": user.lop_leave_days,
        "department": user.department,
        "profilePic": str(user.profilePic) if user.profilePic else "N/A",
        "isReportingManager": user.isReportingManager,
        "reporting_manager": full_name_of_reporting_manager,
        "can_add_employees": user.can_add_employees,
        "can_remove_employees": user.can_remove_employees,
        "can_update_employees": user.can_update_employees,
        "can_read_holidays": user.can_read_holidays,
        "can_write_holidays": user.can_write_holidays,
        "can_create_holidays": user.can_create_holidays,
        "can_delete_holidays": user.can_delete_holidays,
        "can_import_holidays": user.can_import_holidays,
        "can_export_holidays": user.can_export_holidays,
        "can_acceptOrReject_leaves": user.can_acceptOrReject_leaves,
        "can_read_leaves": user.can_read_leaves,
        "can_write_leaves": user.can_write_leaves,
        "can_create_leaves": user.can_create_leaves,
        "can_delete_leaves": user.can_delete_leaves,
        "can_import_leaves": user.can_import_leaves,
        "can_export_leaves": user.can_export_leaves,
        "can_read_clients": user.can_read_clients,
        "can_write_clients": user.can_write_clients,
        "can_create_clients": user.can_create_clients,
        "can_delete_clients": user.can_delete_clients,
        "can_import_clients": user.can_import_clients,
        "can_export_clients": user.can_export_clients,
        "can_read_projects": user.can_read_projects,
        "can_write_projects": user.can_write_projects,
        "can_create_projects": user.can_create_projects,
        "can_delete_projects": user.can_delete_projects,
        "can_import_projects": user.can_import_projects,
        "can_export_projects": user.can_export_projects,
        "can_read_tasks": user.can_read_tasks,
        "can_write_tasks": user.can_write_tasks,
        "can_create_tasks": user.can_create_tasks,
        "can_delete_tasks": user.can_delete_tasks,
        "can_import_tasks": user.can_import_tasks,
        "can_export_tasks": user.can_export_tasks,
        "can_read_chats": user.can_read_chats,
        "can_write_chats": user.can_write_chats,
        "can_create_chats": user.can_create_chats,
        "can_delete_chats": user.can_delete_chats,
        "can_import_chats": user.can_import_chats,
        "can_export_chats": user.can_export_chats,
        "can_read_assets": user.can_read_assets,
        "can_create_assets": user.can_create_assets,
        "can_write_assets": user.can_write_assets,
        "can_delete_assets": user.can_delete_assets,
        "can_import_assets": user.can_import_assets,
        "can_export_assets": user.can_export_assets,
        "can_read_timing_sheets": user.can_read_timing_sheets,
        "can_write_timing_sheets": user.can_write_timing_sheets,
        "can_create_timing_sheets": user.can_create_timing_sheets,
        "can_delete_timing_sheets": user.can_delete_timing_sheets,
        "can_import_timing_sheets": user.can_import_timing_sheets,
        "can_export_timing_sheets": user.can_export_timing_sheets,
        "designation": user.designation 
        }
    
    return JsonResponse({"data":userDetails})
    


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_leave(request):
    user = request.user
    data = request.data
    fullName = user.first_name+" "+user.last_name
    empCode = user.emplyeeIdentficationCode

    leave_type = data.get('leave_type')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    reason = data.get('leave_reason')

    return add_leave_with_calculation(user, leave_type, start_date_str, end_date_str, reason,fullName, empCode, user.username, user.id)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leave_history(request):
    user = request.user
    leave_history = Leave.objects.filter(user=user)
    leave_data = [
        {
            'leave_type': leave.leave_type,
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'leaveStatus': leave.leave_status,
            'approvedBy':leave.processedBy,
            'leaveId':leave.id,
            'userId':leave.user_id
        }
        for leave in leave_history
    ]
    return Response(leave_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_leave(request):
    if request.user.isAdmin != True or request.user.can_acceptOrReject_leaves != True:    
        leave_id = request.data.get('leave_id')
        action = request.data.get('action')  # 'approve' or 'reject' or 'cancel'

        try:
            leave = Leave.objects.get(id=leave_id)
            if not leave:
                return JsonResponse({
                    "message":"Leave request is not found. Reason : Might be a deleted request or invalid request"
                }, status = status.HTTP_404_NOT_FOUND)
            
            userId = leave.user_id
            user = User.objects.get(id=userId)
            if action == 'delete' and leave.leave_status == 'Cancelled':
                leave.delete()
                leave.save()
                return JsonResponse({"message": "Leave request deleted successfully"}, status=status.HTTP_200_OK)
            
            if leave.leavePrecessed == True:
                return JsonResponse({
                    "message":f"Leave Request already processed - {leave.leave_status}",
                },status = status.HTTP_409_CONFLICT)

            if action == 'approve':
                leave.approved = True
                leave.leave_status = "Approved"
                leave.leavePrecessed = True
                leave.processedBy = request.user.first_name+" "+request.user.last_name
                leave.save()
                return JsonResponse({"message": "Leave request approved successfully"}, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                start_date = leave.start_date
                end_date = leave.end_date
                leave_days = leave.noOfDays
                leave_type = leave.leave_type
                leave.processedBy = request.user.first_name+" "+request.user.last_name
                setattr(user, f"{leave_type}_leave_days", F(f"{leave_type}_leave_days") + leave_days)
                user.save()
                leave.approved = False
                leave.leave_status = "Rejected"
                leave.leavePrecessed = True
                leave.save()
                return JsonResponse({"message": "Leave request rejected successfully"}, status=status.HTTP_200_OK)
            
            elif action == 'cancel':
                start_date = leave.start_date
                end_date = leave.end_date
                leave_days = leave.noOfDays
                leave_type = leave.leave_type
                setattr(user, f"{leave_type}_leave_days", F(f"{leave_type}_leave_days") + leave_days)
                user.save()
                leave.approved = False
                leave.leave_status = "Cancelled"
                leave.processedBy = request.user.first_name+" "+request.user.last_name
                leave.leavePrecessed = True
                leave.save()
                return JsonResponse({"message": "Leave request cancelled successfully"}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"message": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)
        except Leave.DoesNotExist:
            return JsonResponse({"message": "Leave not found or you do not have permission to process it"}, status=status.HTTP_404_NOT_FOUND)

    return JsonResponse({
        "message":"Not Authorized",
    },
    status = status.HTTP_401_UNAUTHORIZED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_leave_data(request):
    # Query the Leave model to get the required data
    leave_data = Leave.objects.values('id','user__id', 'user__username','user__emplyeeIdentficationCode', 'start_date', 'end_date','leave_status','leave_type','leavePrecessed','processedBy')

    return JsonResponse(list(leave_data), safe=False, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_holiday(request):
    if request.method == 'POST' and request.user.isAdmin == True:  # Note the change from request.isAdmin to request.user.isAdmin
        data = json.loads(request.body)
        date_str = data['date']
        name = data['name']

        if not date_str:
            return JsonResponse({"message": "Date is required"}, status=400)
        
        # Call the add_holiday function from holiday_management.py
        result, status_code = add_holidayy(date_str, name)

        return JsonResponse(result, status=status_code)
    
    return JsonResponse({"message": "Method not allowed"}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_holidays(request):
    holidays = Holiday.objects.all()
    holidays_list = [{"date": holiday.date.strftime('%Y-%m-%d'), "name": holiday.name} for holiday in holidays]
    return JsonResponse({"holidays": holidays_list})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def punch_in_view(request):
    user = request.user
    current_time, current_date = get_current_time_and_date()

    # check already punched
    try:
        attendance_record = Attendance.objects.get(user=user, date=current_date)
        punch_times = attendance_record.punch_times

        if len(punch_times) % 2 != 0:
            return JsonResponse({"message": "You must punch out before punching in again"}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(punch_times) >= 24:
            return JsonResponse({"message": "Limit Exceded. You have already punched in and out 12 times today"}, status=status.HTTP_400_BAD_REQUEST)

        punch_times.append(current_time.strftime('%H:%M:%S'))
        attendance_record.punch_times = punch_times
        attendance_record.save()
    except Attendance.DoesNotExist:
        # First Punch In
        attendance_record = Attendance.objects.create(user=user, date=current_date, punch_times=[current_time.strftime('%H:%M:%S')], first_punch_in =current_time )

    return JsonResponse({
        "message": "Punch-in recorded successfully",
        "initialPuchedInAt":attendance_record.first_punch_in,
        "punch_in_time": current_time.strftime('%H:%M:%S'),
        "totalPunchTIme":attendance_record.total_punch_time,
        "date":current_date,
        "is_holiday": attendance_record.is_holiday
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def punch_out_view(request):
    user = request.user
    current_time, current_date = get_current_time_and_date()

    try:
        attendance_record = Attendance.objects.get(user=user, date=current_date)
        punch_times = attendance_record.punch_times

        if len(punch_times) % 2 != 1:
            return JsonResponse({"message": "You must punch in before punching out"}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(punch_times) >= 24:
            return JsonResponse({"message": "Limit Exceeded. You have already punched in and out 12 times today"}, status=status.HTTP_400_BAD_REQUEST)
        
        punch_times.append(current_time.strftime('%H:%M:%S'))
        attendance_record.punch_times = punch_times

        # Total Punch time
        total_punch_time = timezone.timedelta()
        for i in range(0, len(punch_times), 2):
            punch_in_time = datetime.strptime(punch_times[i], '%H:%M:%S')
            punch_out_time = datetime.strptime(punch_times[i + 1], '%H:%M:%S')
            punch_duration = punch_out_time - punch_in_time
            total_punch_time += punch_duration


        attendance_record.total_punch_time = total_punch_time
        attendance_record.last_punchout = (punch_times)[-1]
        attendance_record.save()

        return JsonResponse({
            "message": "Punch-out recorded successfully",
            "date":current_date,
            "punch_out_time": current_time.strftime('%H:%M:%S'),
            "lastPunchOut":(punch_times)[-1],
            "total_punch_time": str(total_punch_time)
        }, status=status.HTTP_201_CREATED)

    except Attendance.DoesNotExist:
        return JsonResponse({
            "message": "No corresponding attendance record found"
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_attendance_data(request):
    userId = (json.loads(request.body))['id']
    attendance_data = Attendance.objects.filter(user_id=userId)

    

    data = []
    for attendance in attendance_data:
        data.append({
            'date': attendance.date,
            'punch_times': attendance.punch_times,
            'first_punch_in': attendance.first_punch_in,
            'last_punchout': attendance.last_punchout,
            'total_punch_time': attendance.total_punch_time.total_seconds() / 3600,  # Convert to hours
        })

    # if len(attendance.punch_times)%2 == 0:
    #     lastPunchout = Attendance(last_punchout=((attendance.punch_times)[-1]), user_id = userId)
    #     lastPunchout.save()

    return JsonResponse(data, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def currentDayAttendanceActivity(request):
    current_date = timezone.now().date()
    userId = (json.loads(request.body))['id']
    data = list(Attendance.objects.filter(user_id = userId,date=current_date).values('punch_times'))
    allPuncnchTimesToList = data[0]['punch_times']

    punch_dict = {}
    for i in range(1, len(allPuncnchTimesToList)):
        if i % 2 == 0:
            punch_dict[f'punchOut-{i//2}'] = allPuncnchTimesToList[i]
        else:
            punch_dict[f'punchIn-{(i+1)//2}'] = allPuncnchTimesToList[i]



    return JsonResponse({
        "data": punch_dict
    },status = status.HTTP_200_OK)

    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def profilePicApi(request):
    if request.method == 'POST':
        user = request.user
        image = request.FILES.get('image')

        if not image:
            return JsonResponse({'error': 'Image is required.'}, status=400)

        try:
            user.profilePic = image
            user.save()
            return JsonResponse({'success': 'Image uploaded successfully.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_ReportingManagers(request):
    managers = User.objects.filter(isReportingManager = True)
    managersList = []

    for i in managers:
        managersList.append(i.username)

    return JsonResponse({
        "data" : managersList
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def currentLeaves(request):
    userId = request.user.id

    userObj = User.objects.get(id=userId)
 
    RCLD = userObj.casual_leave_days # casual
    RMLD = userObj.medical_leave_days # medical
    RLOPD = userObj.lop_leave_days # Lop

    return JsonResponse({
        "casual_remaining":RCLD,
        "medical leaves remaining":RMLD,
        "remaining LOP":RLOPD
    }, status = status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_payslip(request):
    id = (json.loads(request.body))['id']
    current_date = datetime.now()
    month = current_date.month
    year = current_date.year
    
    try:
        user = User.objects.get(id=id)
        
        # Check if a payslip has already been generated for the user in the current month and year
        existing_payslip = Payslip.objects.filter(user=user, month=month, year=year).first()
        if existing_payslip:
            return JsonResponse({
                "status": "Failed",
                "message": "Payslip already generated for this user in the current month and year"
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Generate payslip and get S3 URL
        payslip_url = generatePayslip(user)
        
        # Save payslip information in the database
        Payslip.objects.create(user=user, month=month, year=year, s3_url=(json.loads(payslip_url.content))['data'])
        
        return JsonResponse({
            "status": "Success",
            "message": "Salary Slip is generated and mail sent to the Employee"
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkPayslipGeneration(request):
    try:
        users = User.objects.all()
        current_date = datetime.now()
        month = current_date.month
        year = current_date.year

        def generate_payslip_and_save_url(user):
            try:
                response = generatePayslip(user)
                s3_url = (json.loads(response.content))['data']

                # Save payslip information in the database within a transaction
                with transaction.atomic():
                    Payslip.objects.create(user=user, month=month, year=year, s3_url=s3_url)

                return {
                    "username": user.username,
                    "employee_id": user.emplyeeIdentficationCode,
                    "designation": user.designation,
                    "s3_url": s3_url
                }
            except Exception as e:
                return {
                    "username": user.username,
                    "employee_id": user.emplyeeIdentficationCode,
                    "designation": user.designation,
                    "error_message": str(e)
                }

        success_cases = []
        failure_cases = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_payslip_and_save_url, user) for user in users]

            for future in futures:
                result = future.result()
                if "error_message" in result:
                    failure_cases.append(result)
                else:
                    success_cases.append(result)

        if success_cases:
            send_email_payslipData(success_cases, True)

        if failure_cases:
            send_email_payslipData(failure_cases, False)

        return JsonResponse({
            "status": "Success",
            "message": f"{len(success_cases)} payslips generated successfully, {len(failure_cases)} failed",
            "success_cases": success_cases,
            "failure_cases": failure_cases
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
