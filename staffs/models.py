from django.db import models
import uuid
from django.core.validators import RegexValidator

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "FEMALE"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        TERMINATED = "terminated", "Terminated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_id = models.CharField(max_length=20, unique=True, db_index=True)

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(
        max_length=15, validators=[RegexValidator(r'^\+?\d{9, 15}$')], blank=True
    )
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="staffs")
    position = models.CharField(max_length=100, blank=True)

    fingerprint_template = models.BinaryField(null=True, blank=True)
    device_user_id = models.PositiveIntegerField(null=True, blank=True, unique=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["staff_id"]

    def __str__(self):
        return f"{self.staff_id} - {self.first_name} {self.last_name}"