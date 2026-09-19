from django.contrib import admin
from .models import AdminProfile

admin.site.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "department"]
    list_filter = ["role", "department"]