from rest_framework.routers import DefaultRouter

from apps.transactions.views import CreateCompanyTransactionViewSet, CreatePersonTransactionViewSet

router = DefaultRouter()
router.register(r'transactions/company', CreateCompanyTransactionViewSet)
router.register(r'transactions/person', CreatePersonTransactionViewSet)
