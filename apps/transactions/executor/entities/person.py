from apps.accounts.models import PersonAccount
from apps.transactions.models import PersonTransaction


class PersonEntity:
    def __init__(self, account):
        self.account = account
        self.account_instance = self.get_account_instance()

    def get_account_instance(self):
        return PersonAccount.objects.filter(pk=self.account.number).first()

    def get_email(self):
        return (self.account_instance.user.email
                if hasattr(self.account_instance, 'user') else None)

    def get_owner_id(self):
        return (self.account_instance.user.cpf
                if hasattr(self.account_instance, 'user') else None)

    def get_user_data(self):
        return (self.account_instance.user
                if hasattr(self.account_instance, 'user') else None)

    def get_transaction_model(self):
        return PersonTransaction
