from apps.accounts.models import CompanyAccount
from apps.transactions.models import CompanyTransaction


class CompanyEntity:
    def __init__(self, account):
        self.account = account
        self.account_instance = self.get_account_instance()

    def get_account_instance(self):
        return CompanyAccount.objects.filter(pk=self.account.number).first()

    def get_email(self):
        return (self.account_instance.company.user.email
                if hasattr(self.account_instance, 'company') else None)

    def get_owner_id(self):
        return (self.account_instance.company.cnpj
                if hasattr(self.account_instance, 'company') else None)

    def get_user_data(self):
        return (self.account_instance.company
                if hasattr(self.account_instance, 'company') else None)

    def get_transaction_model(self):
        return CompanyTransaction
