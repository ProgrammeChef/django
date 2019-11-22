from django.core.validators import MinValueValidator
from django.db import models

from django_ledger.models.mixins.base import CreateUpdateMixIn


class TransactionModelAbstract(CreateUpdateMixIn):
    TX_TYPE = [
        ('credit', 'Credit'),
        ('debit', 'Debit')
    ]

    tx_type = models.CharField(max_length=10, choices=TX_TYPE)
    journal_entry = models.ForeignKey('django_ledger.JournalEntryModel',
                                      related_name='txs',
                                      on_delete=models.CASCADE)

    account = models.ForeignKey('django_ledger.AccountModel',
                                related_name='txs',
                                on_delete=models.PROTECT)

    amount = models.DecimalField(decimal_places=2,
                                 max_digits=20,
                                 null=True,
                                 blank=True,
                                 validators=[
                                     MinValueValidator(0)
                                 ])
    description = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tx Description')

    class Meta:
        abstract = True

    def __str__(self):
        return '{x1}-{x2}/{x5}: {x3}/{x4}'.format(x1=self.account.code,
                                                  x2=self.account.name,
                                                  x3=self.amount,
                                                  x4=self.tx_type,
                                                  x5=self.account.balance_type)


class TransactionModel(TransactionModelAbstract):
    """
    Final TransactionModel from Abstracts
    """
