from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Department, Staff
from .serializers import DepartmentSerializer, StaffSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


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
            staff.fingerprint_enrolled = fingerprint_template

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
