from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .utils import *

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=10, min_length=6, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 
                  'username', 
                  'password', 
                  'first_name', 
                  'last_name',
                  'emplyeeIdentficationCode',  
                  'joining_date', 
                  'phone', 
                  'department', 
                  'designation',
                  'isReportingManager',
                  'isAdmin',
                  'salary',
                  'casual_leave_days',
                  'medical_leave_days',
                  'lop_leave_days',
                  'can_read_holidays',
                  'can_write_holidays',
                  'can_create_holidays',
                  'can_delete_holidays',
                  'can_import_holidays',
                  'can_export_holidays',
                  'can_read_leaves',
                  'can_write_leaves',
                  'can_create_leaves',
                  'can_delete_leaves',
                  'can_import_leaves',
                  'can_export_leaves',
                  'can_read_clients',
                  'can_write_clients',
                  'can_create_clients',
                  'can_delete_clients',
                  'can_import_clients',
                  'can_export_clients',
                  'can_read_projects',
                  'can_write_projects',
                  'can_create_projects',
                  'can_delete_projects',
                  'can_import_projects',
                  'can_export_projects',
                  'can_read_tasks',
                  'can_write_tasks',
                  'can_create_tasks',
                  'can_delete_tasks',
                  'can_import_tasks',
                  'can_export_tasks',
                  'can_read_chats',
                  'can_write_chats',
                  'can_create_chats',
                  'can_delete_chats',
                  'can_import_chats',
                  'can_export_chats',
                  'can_read_assets',
                  'can_create_assets',
                  'can_write_assets',
                  'can_delete_assets',
                  'can_import_assets',
                  'can_export_assets',
                  'can_read_timing_sheets',
                  'can_write_timing_sheets',
                  'can_create_timing_sheets',
                  'can_delete_timing_sheets',
                  'can_import_timing_sheets',
                  'can_export_timing_sheets',
                #   'reporting_manager',
                  'basic_salary',
                  'hra',
                  'pf',
                  'special_allowances',
                  'isReportingManager',
                  'can_add_employees',
                  'can_remove_employees',
                  'can_update_employees',
                  'isOwner'
                  ]
    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs 
    def create(self, validated_data):
        if 'emplyeeIdentficationCode' not in validated_data or validated_data['emplyeeIdentficationCode'] == '0':
            validated_data['emplyeeIdentficationCode'] = generate_employee_code() 
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6,write_only=True)
    username = serializers.CharField(max_length=255, min_length=3)
    tokens = serializers.SerializerMethodField()
    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }
    class Meta:
        model = User
        fields = ['password','username','tokens']
    def validate(self, attrs):
        username = attrs.get('username','')
        password = attrs.get('password','')
        user = auth.authenticate(username=username,password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')