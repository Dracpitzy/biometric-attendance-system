from rest_framework import serializers
from .models import Department, Staff

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class StaffSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    fingerprint_enrolled = serializers.SerializerMethodField()

    class Meta:
        model =  Staff
        fields = [
            "id", "staff_id", "first_name", "last_name", "phone_number", "gender", "department", "department_name", "position", "device_user_id",
            "fingerprint_enrolled", "status", "date_joined", "is_active", "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "date_joined", "created_at", "updated_at"]
        extra_kwargs = {
            "device_user_id": {"write_only": True},
        }

    def get_fingerprint_enrolled(self, obj):
        return bool(obj.device_user_id or obj.fingerprint_template)