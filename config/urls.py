from django.contrib import admin
from django.urls import include, path
from staffs.views import staff_register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/staffs/', include('staffs.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('register/', staff_register, name='staff-register'),
]
