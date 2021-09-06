import logging

from apps.transactions.executor.transaction import Transaction


class UseCreditTransaction(Transaction):
    def process(self):
        credit_outlay = self.account_instance.credit_outlay
        self.credit_expires = self.account_instance.credit_expires
        self.credit_fees = self.calculate_credit_fees(self.credit_expires)

        transaction_canceled_data = {'status': 'canceled',
                                     'transaction_type': self.transaction_type,
                                     'amount': self.amount}

        if self.credit_fees:
            logging.info('UseCredit transaction canceled. Is need to pay the credit outlay and fees in order to use credit again')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'debitor',
                                'note': 'Is need to pay the credit outlay and fees in order to use credit again'})

        if (credit_outlay + self.amount) > self.account_instance.credit_limit:
            logging.info('UseCredit transaction canceled. Limit of credit achieved')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'limit',
                                'note': 'Limit of credit achieved'})

        self.account_instance.credit_outlay = + self.amount

        logging.info('UseCredit transaction done')
        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})
