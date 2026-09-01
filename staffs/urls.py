from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, StaffViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet)
router.register(r"staff", StaffViewSet)

urlpatterns = router.urls