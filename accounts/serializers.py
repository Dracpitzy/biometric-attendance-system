from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AdminProfile


class AdminProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    role_display = serializers.CharField(source="get_role_display")
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)

    class Meta:
        model = AdminProfile
        fields = [
            "id", "username", "email", "role", "role_display",
            "department", "department_name",
        ]


class AdminProfileCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = AdminProfile
        fields = ["username", "email", "password", "role", "department"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return AdminProfile.objects.create(
            user=user,
            role=validated_data["role"],
            department=validated_data.get("department"),
        )