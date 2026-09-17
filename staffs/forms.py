from django.db.models import Count
from django import forms
from .models import Staff, Department


class StaffRegistrationForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select department",
    )

    class Meta:
        model = Staff
        fields = ["first_name", "last_name", "phone_number", "gender", "department", "position"]

    def save(self, commit=True):
        staff = super().save(commit=False)
        staff.staff_id = self._generate_staff_id(staff.department)
        if commit:
            staff.save()
        return staff

    def _generate_staff_id(self, department):
        prefix = department.name[:3].upper()
        count = Staff.objects.filter(department=department).count()
        return f"{prefix}-{count + 1:04d}"