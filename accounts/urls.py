from django.urls import path
from .views import AdminLoginView, AdminProfileListCreateView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("admins/", AdminProfileListCreateView.as_view(), name="admin-list-create"),
]