from common.permissions import IsBackOffice, IsUserCompany
from rest_framework import generics, viewsets

from apps.accounts.models import CompanyAccount, PersonAccount

from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(generics.CreateAPIView,
                     generics.RetrieveAPIView,
                     generics.DestroyAPIView,
                     viewsets.ViewSet):
    queryset = Company.objects.all()
    http_method_names = ['post', 'get', 'delete', 'head']
    serializer_class = CompanySerializer

    class Meta:
        model = PersonAccount

    def get_permissions(self):
        self.permission_classes = [IsUserCompany]

        if (self.request.method in ['POST', 'DELETE'] or
                (self.request.method == 'GET' and not bool(self.kwargs))):
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()
