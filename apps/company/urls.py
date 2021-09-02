from rest_framework.routers import DefaultRouter

from apps.company.views import CompanyViewSet

router = DefaultRouter()
router.register(r'company', CompanyViewSet)
