from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render

from .forms import StaffRegistrationForm
from .models import Department, Staff
from .serializers import DepartmentSerializer, StaffSerializer
from accounts.permissions import IsSuperAdmin, IsAnyAdmin, IsSuperAdminOrReadOnly


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsSuperAdminOrReadOnly]


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    @action(detail=True, methods=["post"], url_path="enroll-fingerprint")
    def enroll_fingerprint(self, request, pk=None):
        staff = self.get_object()

        device_user_id = request.data.get("device_user_id")
        fingerprint_template = request.data.get("fingerprint_template")

        if not device_user_id and not fingerprint_template:
            return Response(
                {"error": "device_user_id or fingerprint_template is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if device_user_id:
            staff.device_user_id = device_user_id
        if fingerprint_template:
            staff.fingerprint_template = fingerprint_template

        staff.save()
        return Response(
            {"message": "Fingerprint enrolled successfully."}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="remove-fingerprint")
    def remove_fingerprint(self, request, pk=None):
        staff = self.get_object()
        staff.device_user_id = None
        staff.fingerprint_template = None
        staff.save()
        return Response(
            {"message": "Fingerprint enrollment removed."}, 
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, methods=["patch"], url_path="update-status",
        permission_classes=[IsSuperAdmin],
    )
    def update_status(self, request, pk=None):
        staff = self.get_object()
        new_status = request.data.get("status")
        valid_statuses = [choice[0] for choice in Staff.Status.choices]

        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        staff.status = new_status
        staff.save()
        return Response(
            {"message": f"Status updated to {staff.get_status_display()}."},
            status=status.HTTP_200_OK,
        )

    
    @action(
        detail=False, methods=["get"], url_path="pending-enrollment",
        permission_classes=[IsAnyAdmin],
    )
    def pending_enrollment(self, request):
        queryset = Staff.objects.filter(
            device_user_id__isnull=True, fingerprint_template__isnull=True, is_active=True
        )

        admin_profile = request.user.admin_profile
        if admin_profile.role == "department_head":
            queryset = queryset.filter(department=admin_profile.department)

        serializer = StaffSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



def staff_register(request):
    if request.method == "POST":
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            staff = form.save()
            return render(request, "staffs/register_success.html", {"staff": staff})
    else:
        form = StaffRegistrationForm()
    return render(request, "staffs/register.html", {"form": form})