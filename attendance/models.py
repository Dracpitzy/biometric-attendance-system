import uuid
from django.db import models
from staffs.models import Staff

class AttendanceLog(models.Model):
    class LogType(models.TextChoices):
        CHECK_IN = "check_in", "Check In"
        CHECK_OUT = "check_out", "Check Out"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="attendance_logs")
    log_type = models.CharField(max_length=10, choices=LogType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.staff.staff_id} - {self.log_type} @ {self.timestamp}"




