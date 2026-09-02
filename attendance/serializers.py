from rest_framework import  serializers
from .model import AttendanceLog

class AttendanceLogSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.first_name", read_only=True)
    staff_id_display = serializers.CharField(source="staff.staff_id", read_only=True)

    class Meta:
        model = AttendanceLog
        fields = [
            "id",
            "staff",
            "staff_id_display",
            "staff_name",
            "log_type",
            "timestamp",
        ]
        read_only_fields = ["id", "log_type", "timestamp"]