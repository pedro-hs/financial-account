import logging

from apps.accounts.constants import ACCOUNT_TYPES
from apps.transactions.constants import TRANSACTION_TYPES
from common.errors import BadRequest

from .transactions import deposit, pay_credit, use_credit, withdrawal

TRANSACTIONS = {'deposit': deposit.DepositTransaction,
                'withdrawal': withdrawal.WithDrawalTransaction,
                'use_credit': use_credit.UseCreditTransaction,
                'pay_credit': pay_credit.PayCreditTransaction}


class TransactionExecutor:
    def __init__(self, account, amount, transaction_type):
        self.transaction_type = transaction_type
        self.account = account
        self.account_type_status = [hasattr(self.account, account_type)
                                    for account_type in ACCOUNT_TYPES]
        self.account_type = self.get_account_type()
        self.amount = amount

        logging.info('Processing %s transaction for %s', transaction_type, self.account_type)

    def process(self):
        self.validate_data()
        return self.execute_transaction()

    def validate_data(self):
        if self.transaction_type not in TRANSACTION_TYPES:
            raise BadRequest('Invalid transaction_type')

        if self.amount < 1:
            raise BadRequest('Invalid amount')

        account_owners = self.account_type_status.count(True)

        if account_owners > 1:
            raise BadRequest("Invalid account. Account can't have more than one owner")

        elif account_owners < 1:
            raise BadRequest('Invalid account. Account need to have an owner')

    def get_account_type(self):
        transaction_type_index = self.account_type_status.index(True)
        return ACCOUNT_TYPES[transaction_type_index]

    def execute_transaction(self):
        return TRANSACTIONS[self.transaction_type](self.account, self.amount,
                                                   self.transaction_type, self.account_type).execute()
