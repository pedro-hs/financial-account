from common.permissions import IsBackOffice, IsUserBase
from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response

from .models import User
from .serializers import DefaultUserSerializer, PostUserSerializer, PutUserSerializer


class IsUser(IsUserBase):
    def has_object_permission(self, request, view, instance):
        if request.user.role == 'collaborator':
            return True

        return request.user.role == 'customer' and instance == request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    serializer_class = DefaultUserSerializer

    class Meta:
        model = User

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.Meta.model(**serializer.data)
        password = request.data['password']
        instance.set_password(password)
        instance.save()

        data = DefaultUserSerializer(instance).data
        headers = self.get_success_headers(data)
        return Response(data, status=201, headers=headers)

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_permissions(self):
        self.permission_classes = [IsUser]

        if (self.request.method in ['POST', 'DELETE'] or
                (self.request.method == 'GET' and not bool(self.kwargs))):
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()

    def get_serializer_class(self):
        get_serializer = {'update': PutUserSerializer,
                          'create': PostUserSerializer}
        return get_serializer.get(self.action, DefaultUserSerializer)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def perform_update(self, serializer):
        if serializer.validated_data.get('role', 'user') == 'collaborator':
            serializer.validated_data['is_staff'] = True

        serializer.save()
