from rest_framework.routers import DefaultRouter

from apps.accounts.views import CompanyAccountViewSet, PersonAccountViewSet

router = DefaultRouter()
router.register(r'accounts/person', PersonAccountViewSet)
router.register(r'accounts/company', CompanyAccountViewSet)
