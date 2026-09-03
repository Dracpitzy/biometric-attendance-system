from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings

from .models import AttendanceLog


def generate_weekly_attendance_report():
    today = timezone.localdate()
    week_start = today - timedelta(days=7)

    logs = (
        AttendanceLog.objects.filter(timestamp__date__gte=week_start, timestamp__date__lte=today).select_related("staff").order_by("staff__staff_id", "timestamp")
    )

    lines = [f"Weeekly Attendance Report: {week_start} to {today}", ""]

    if not logs.exists():
        lines.append("No attendance record for this period.")
    else:
        for log in logs:
            line.append(
                f"{log.staff.staff_id} - {log.staff.first_name} {log.staff.last_name} | "
                f"{log.get_log_type_display()} | {timezone.localtime(log.timestamp).strftime('%Y-%m-%d %H:%M')}"
            )

    return "\n".join(lines)

def send_weekly_attendance_email():
    report_body = generate_weekly_attendance_report

    email = EmailMessage(
        subject=f"Weekly Attendance Report - {timezone.localdate().strftime('%Y-%m-%d')}",
        body=report_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_EMAIL],
    ) 
    email.send()