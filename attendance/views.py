from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from staffs.models import Staff
from .models import AttendanceLog
from .serializers import AttendanceLogSerializer


class AttendanceLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceLog.objects.all()
    serializer_class = AttendanceLogSerializer

    @action(detail=False, methods=["post"], url_path="scan")
    def scan(self, request):
        device_user_id = request.data.get("device_user_id")

        if not device_user_id:
            return Response(
                {"error": "device_user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            staff = Staff.objects.get(device_user_id=device_user_id, is_active=True)
        except Staff.DoesNotExist:
            return Response(
                {"error": "No active staff found for this fingerprint"},
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.localdate()
        todays_logs = AttendanceLog.objects.filter(staff=staff, timestamp__date=today)

        already_checked_in = todays_logs.filter(log_type=AttendanceLog.LogType.CHECK_IN).exists()
        already_checked_out = todays_logs.filter(log_type=AttendanceLog.LogType.CHECK_OUT).exists()

        if not already_checked_in:
            log_type = AttendanceLog.LogType.CHECK_IN
        elif not already_checked_out:
            log_type = AttendanceLog.LogType.CHECK_OUT
        else:
            return Response(
                {"error": f"{staff.first_name} has already checked in and out today."},
                status=status.HTTP_400_BAD_REQUEST
            )

        log = AttendanceLog.objects.create(
            staff=staff, log_type=log_type
        )
        serializer = AttendanceLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="currently-in")
    def currently_in(self, request):
        today = timezone.localdate()

        checked_in_ids = (
            AttendanceLog.objects.filter(timestamp__date=today, log_type=AttendanceLog.LogType.CHECK_IN).values_list("staff_id", flat=True)
        )
        checked_out_ids = (
            AttendanceLog.objects.filter(timestamp__date=today, log_type=AttendanceLog.LogType.CHECK_OUT).values_list("staff_id", flat=True)
        )
        currrently_in_ids = set(checked_in_ids) - set(checked_out_ids)

        staff = Staff.objects.filter(id__in=currrently_in_ids, is_active=True)

        from staffs.serializers import StaffSerializer
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    


