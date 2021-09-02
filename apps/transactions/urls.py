from rest_framework.routers import DefaultRouter

from apps.transactions.views import (CreateCompanyTransactionViewSet,
                                     CreatePersonTransactionViewSet, ListCompanyTransactionsViewSet,
                                     ListPersonTransactionsViewSet)

router = DefaultRouter()
router.register(r'transactions/company', CreateCompanyTransactionViewSet)
router.register(r'transactions/person', CreatePersonTransactionViewSet)
router.register(r'transactions/company/list', ListCompanyTransactionsViewSet)
router.register(r'transactions/person/list', ListPersonTransactionsViewSet)
