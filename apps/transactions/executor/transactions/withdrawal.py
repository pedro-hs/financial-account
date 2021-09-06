import logging

from apps.transactions.executor.transaction import Transaction


class WithDrawalTransaction(Transaction):
    def process(self):
        balance = self.account_instance.balance

        transaction_canceled_data = {'status': 'canceled',
                                     'transaction_type': self.transaction_type,
                                     'amount': self.amount}

        if self.amount > balance:
            logging.info('WithDrawal transaction canceled. Fund is lower than balance')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'insufficient_fund',
                                'note': 'Fund is lower than balance'})

        if self.amount > self.account_instance.withdrawal_limit:
            logging.info('WithDrawal transaction canceled. Limit of withdrawal achieved')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'limit',
                                'note': 'Limit of withdrawal achieved'})

        self.account_instance.balance = balance - self.amount

        logging.info('WithDrawal transaction done')
        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})
