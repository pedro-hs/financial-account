import logging

from apps.transactions.executor.transaction import Transaction


class DepositTransaction(Transaction):
    def process(self):
        self.account_instance.balance = self.account_instance.balance + self.amount

        logging.info('Deposit transaction done')
        return self.create('done', self.amount)
