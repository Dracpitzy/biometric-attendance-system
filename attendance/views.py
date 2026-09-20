from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import calendar
from datetime import date
from django.shortcuts import render
from django.db.models import Count

from staffs.models import Staff
from .models import AttendanceLog
from .serializers import AttendanceLogSerializer
from staffs.models import Department
from accounts.permissions import IsAnyAdmin


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


    def get_queryset(self):
        queryset = AttendanceLog.objects.all()
        staff_id = self.request.query_params.get("staff")
        department_id = self.request.query_params.get("department")
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        if department_id:
            queryset = queryset.filter(staff__department_id=department_id)

        user = self.request.user
        if user.is_authenticated and hasattr(user, "admin_profile"):
            if user.admin_profile.role == "department_head":
                queryset = queryset.filter(staff__department=user.admin_profile.department)

        return queryset



    @action(
        detail=False, methods=["get"], url_path="today-summary",
        permission_classes=[IsAnyAdmin],
    )
    def today_summary(self, request):
        today = timezone.localdate()
        admin_profile = request.user.admin_profile

        staff_qs = Staff.objects.filter(is_active=True)
        if admin_profile.role == "department_head":
            staff_qs = staff_qs.filter(department=admin_profile.department)

        checked_in_ids = set(
            AttendanceLog.objects.filter(
                timestamp__date=today,
                log_type=AttendanceLog.LogType.CHECK_IN,
                staff__in=staff_qs,
            ).values_list("staff_id", flat=True)
        )

        by_department = []
        for dept in Department.objects.filter(staffs__in=staff_qs).distinct():
            dept_staff = staff_qs.filter(department=dept)
            by_department.append({
                "department": dept.name,
                "total_staff": dept_staff.count(),
                "checked_in": dept_staff.filter(id__in=checked_in_ids).count(),
            })

        return Response({
            "date": today,
            "total_active_staff": staff_qs.count(),
            "checked_in_today": len(checked_in_ids),
            "by_department": by_department,
        })

    @action(
        detail=False, methods=["get"], url_path="department-stats",
        permission_classes=[IsAnyAdmin],
    )
    def department_stats(self, request):
        today = timezone.localdate()
        admin_profile = request.user.admin_profile

        departments = Department.objects.all()
        if admin_profile.role == "department_head":
            departments = departments.filter(id=admin_profile.department_id)

        days_elapsed = today.day
        results = []
        for dept in departments:
            staff_qs = Staff.objects.filter(department=dept, is_active=True)
            staff_count = staff_qs.count()
            possible_checkins = staff_count * days_elapsed

            actual_checkins = AttendanceLog.objects.filter(
                staff__in=staff_qs,
                log_type=AttendanceLog.LogType.CHECK_IN,
                timestamp__year=today.year,
                timestamp__month=today.month,
            ).values("staff_id", "timestamp__date").distinct().count()

            rate = round((actual_checkins / possible_checkins) * 100, 1) if possible_checkins else 0

            results.append({
                "department": dept.name,
                "staff_count": staff_count,
                "checkins_this_month": actual_checkins,
                "attendance_rate_percent": rate,
            })

        return Response(results)

    
def attendance_lookup(request):
    staff = None
    error = None
    calendar_weeks = None
    month_name = None
    year = month = None
    prev_month = prev_year = next_month = next_year = None
    can_go_prev = can_go_next = False
    month_choices = []
    year_choices = []

    staff_id = request.GET.get("staff_id", "").strip()

    if staff_id:
        try:
            staff = Staff.objects.get(staff_id__iexact=staff_id)
        except Staff.DoesNotExist:
            error = f"No staff found with ID {staff_id}"

    if staff:
        today = date.today()
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))

        logs = AttendanceLog.objects.filter(
            staff=staff, timestamp__year=year, timestamp__month=month
        )

        day_data = {}
        for log in logs:
            day = log.timestamp.day
            entry = day_data.setdefault(day, {"check_in": None, "check_out": None})
            if log.log_type == AttendanceLog.LogType.CHECK_IN:
                if entry["check_in"] is None or log.timestamp < entry["check_in"]:
                    entry["check_in"] = log.timestamp
            else:
                if entry["check_out"] is None or log.timestamp > entry["check_out"]:
                    entry["check_out"] = log.timestamp

        month_matrix = calendar.monthcalendar(year, month)
        calendar_weeks = []
        for week in month_matrix:
            week_cells = []
            for day in week:
                if day == 0:
                    week_cells.append(None)
                    continue
                cell_date = date(year, month, day)
                info = day_data.get(day)
                if cell_date > today:
                    status = "future"
                elif info and info["check_in"] and info["check_out"]:
                    status = "complete"
                elif info and info["check_in"]:
                    status = "incomplete"
                else:
                    status = "absent"
                week_cells.append({
                    "day": day,
                    "status": status,
                    "is_today": cell_date == today,
                    "check_in": info["check_in"] if info else None,
                    "check_out": info["check_out"] if info else None,
                })
            calendar_weeks.append(week_cells)

        month_name = calendar.month_name[month]

        joined = staff.date_joined
        min_year, min_month = joined.year, joined.month
        max_year, max_month = today.year, today.month

        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year

        if month == 12:
            next_month, next_year = 1, year + 1
        else:
            next_month, next_year = month + 1, year

        can_go_prev = (year, month) > (min_year, min_month)
        can_go_next = (year, month) < (max_year, max_month)

        month_choices = list(enumerate(calendar.month_name))[1:]
        year_choices = list(range(min_year, max_year + 1))

    return render(request, "attendance/attendance_lookup.html", {
        "staff": staff,
        "error": error,
        "staff_id_value": staff_id,
        "calendar_weeks": calendar_weeks,
        "month_name": month_name,
        "year": year,
        "month": month,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "can_go_prev": can_go_prev,
        "can_go_next": can_go_next,
        "month_choices": month_choices,
        "year_choices": year_choices,
    })


def attendance_landing(request):
    return render(request, "attendance/attendance_landing.html")

