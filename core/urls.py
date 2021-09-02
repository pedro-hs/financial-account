from apps.accounts.views import CompanyAccountViewSet, PersonAccountViewSet
from apps.company.views import CompanyViewSet
from apps.transactions.views import (CreateCompanyTransactionViewSet,
                                     CreatePersonTransactionViewSet, ListCompanyTransactionsViewSet,
                                     ListPersonTransactionsViewSet)
from apps.users.views import UserViewSet
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

doc_schema = get_schema_view(
    title='Financial account API',
    renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer]
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'accounts/person', PersonAccountViewSet)
router.register(r'accounts/company', CompanyAccountViewSet)
router.register(r'company', CompanyViewSet)
router.register(r'transactions/accounts/company', CreateCompanyTransactionViewSet)
router.register(r'transactions/accounts/person', CreatePersonTransactionViewSet)
router.register(r'transactions/accounts/company/list', ListCompanyTransactionsViewSet)
router.register(r'transactions/accounts/person/list', ListPersonTransactionsViewSet)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('token/auth/', obtain_jwt_token),
    path('token/refresh/', refresh_jwt_token),
    path('docs/', doc_schema),
    path('', include(router.urls)),
]
