from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AdminProfile
from staffs.models import Staff


class AdminProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    linked_staff_name = serializers.SerializerMethodField()

    class Meta:
        model = AdminProfile
        fields = [
            "id", "username", "email", "role", "role_display",
            "department", "department_name", "linked_staff", "linked_staff_name",
        ]

    def get_linked_staff_name(self, obj):
        if obj.linked_staff:
            return f"{obj.linked_staff.first_name} {obj.linked_staff.last_name}"
        return None


class AdminProfileCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    staff = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(), required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = AdminProfile
        fields = ["username", "email", "password", "role", "department", "staff"]

    def create(self, validated_data):
        staff = validated_data.pop("staff", None)
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return AdminProfile.objects.create(
            user=user,
            role=validated_data["role"],
            department=validated_data.get("department"),
            linked_staff=staff,
        )