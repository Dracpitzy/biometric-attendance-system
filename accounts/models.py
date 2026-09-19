from django.db import models
from django.conf import settings

from staffs.models import Department

class AdminProfile(models.Model):

    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Admin"
        DEPARTMENT_HEAD = "department_head", "Department Head"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=20, choices=Role.choices)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_profiles')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"