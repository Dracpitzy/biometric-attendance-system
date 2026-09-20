from rest_framework import  serializers
from .models import AttendanceLog

class AttendanceLogSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    staff_id_display = serializers.CharField(source="staff.staff_id", read_only=True)
    department_name = serializers.CharField(source="staff.department.name", read_only=True, default=None)

    class Meta:
        model = AttendanceLog
        fields = [
            "id",
            "staff",
            "staff_id_display",
            "staff_name",
            "department_name",
            "log_type",
            "timestamp",
        ]
        read_only_fields = ["id", "log_type", "timestamp"]

    def get_department_name(self, obj):
        return f"{obj.staff.first_name} {obj.staff.last_name}"