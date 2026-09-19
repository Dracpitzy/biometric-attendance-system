from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AdminProfile


class AdminProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    role_dispaly = serializers.CharField(source="get_role_display")
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)

    class Meta:
        model = AdminProfile
        fields = [
            "id", "username", "email", "role", "role_display",
            "department", "department_name",
        ]