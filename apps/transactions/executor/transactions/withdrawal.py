import logging

from apps.transactions.executor.transaction import Transaction


class WithDrawalTransaction(Transaction):
    def process(self):
        balance = self.account_instance.balance

        if self.amount > balance:
            logging.info('WithDrawal transaction canceled. Fund is lower than balance')
            return self.create('canceled', self.amount, canceled_reason='insufficient_fund',
                               note='Fund is lower than balance')

        if self.amount > self.account_instance.withdrawal_limit:
            logging.info('WithDrawal transaction canceled. Limit of withdrawal achieved')
            return self.create('canceled', self.amount, canceled_reason='limit',
                               note='Limit of withdrawal achieved')

        self.account_instance.balance = balance - self.amount

        logging.info('WithDrawal transaction done')
        return self.create('done', self.amount)
