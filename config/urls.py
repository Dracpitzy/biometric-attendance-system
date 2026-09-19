from django.contrib import admin
from django.urls import include, path
from staffs.views import staff_register
from attendance.views import attendance_lookup, attendance_landing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/staffs/', include('staffs.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('register/', staff_register, name='staff-register'),
    path('attendance-check', attendance_lookup, name='attendance-check'),
    path('attendance/', attendance_landing, name='attendance-landing'),
]
