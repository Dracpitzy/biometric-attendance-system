from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django.contrib.auth import authenticate

from .models import AdminProfile
from .permissions import IsSuperAdmin
from .serializers import AdminProfileSerializer, AdminProfileCreateSerializer


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials"}, status=401)

        if not hasattr(user, "admin_profile"):
            return Response({"detail": "This account has no admin access"}, status=403)

        token, _ = Token.objects.get_or_create(user=user)
        profile_data = AdminProfileSerializer(user.admin_profile).data

        return Response({"token": token.key, "admin": profile_data})


class AdminProfileListCreateView(generics.ListCreateAPIView):
    queryset = AdminProfile.objects.select_related("user", "department")
    permission_classes = [IsSuperAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminProfileCreateSerializer
        return AdminProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_profile = serializer.save()
        output_serializer = AdminProfileSerializer(admin_profile)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)



class AdminProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminProfile.objects.select_related("user", "department", "linked_staff")
    serializer_class = AdminProfileSerializer
    permission_classes = [IsSuperAdmin]

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()
