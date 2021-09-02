from apps.accounts.urls import router as accounts_router
from apps.company.urls import router as company_router
from apps.transactions.urls import router as transactions_router
from apps.users.urls import router as users_router
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
for route in [accounts_router, company_router, transactions_router, users_router]:
    router.registry.extend(route.registry)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('token/auth/', obtain_jwt_token),
    path('token/refresh/', refresh_jwt_token),
    path('docs/', doc_schema),
    path('', include(router.urls)),
]
