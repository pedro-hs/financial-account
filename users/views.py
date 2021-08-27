from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class ModelViewSet(viewsets.ModelViewSet):
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    class Meta:
        model = User

    def get_permissions(self):
        self.permission_classes = (IsAdminUser,)

        if self.request.method == 'POST':
            self.permission_classes = (AllowAny,)

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.Meta.model(**serializer.data)
        password = request.data['password']
        instance.set_password(password)
        instance.save()

        data = UserSerializer(instance).data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        if serializer.validated_data.get('role', 'user') == 'admin':
            serializer.validated_data['is_staff'] = True

        serializer.save()

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
