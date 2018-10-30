from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django_pandas.io import read_frame
from pandas import merge

from django_ledger.models.accounts import AccountModel
from django_ledger.models.mixins import CreateUpdateMixIn, SlugNameMixIn


class ChartOfAccountModelAbstract(SlugNameMixIn,
                                  CreateUpdateMixIn):
    desc = models.TextField(verbose_name='CoA Description')
    accounts = models.ManyToManyField('django_ledger.AccountModel',
                                      related_name='coas',
                                      through='CoAAccountAssignments')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    # todo: this is a duplicate from fcts model.
    def get_accounts_index_df(self):
        accounts = AccountModel.objects.all()
        accounts_df = read_frame(accounts,
                                 fieldnames=['acc_role_bs', 'acc_parent', 'acc_code', 'acc_role', 'acc_desc',
                                             'acc_type'])
        parents_df = accounts_df[accounts_df['acc_parent'] == accounts_df['acc_code']][['acc_code', 'acc_desc']]
        parents_df.rename(columns={'acc_desc': 'parent_desc', 'acc_code': 'parent_code'}, inplace=True)
        accounts_df = accounts_df[accounts_df['acc_parent'] != accounts_df['acc_code']]
        accounts_df = merge(left=accounts_df, right=parents_df, left_on='acc_parent', right_on='parent_code')
        accounts_df.drop('acc_parent', axis=1, inplace=True)
        accounts_df['acc_type'] = accounts_df['acc_type'].str.lower()
        accounts_df['acc_role_bs'] = accounts_df['acc_role_bs'].str.upper()
        accounts_df.set_index(keys=['acc_role_bs', 'parent_code', 'parent_desc',
                                    'acc_role', 'acc_code', 'acc_desc', 'acc_type'],
                              inplace=True)
        accounts_df.sort_index(inplace=True)
        return accounts_df


def get_coa_account(coa_model, code):
    try:
        qs = coa_model.acc_assignments.available()
        acc_model = qs.get(account__code__iexact=code)
        return acc_model
    except ObjectDoesNotExist:
        raise ValueError('Account {acc} is either not assigned, inactive, locked or non existent for CoA: {coa}'.format(
            acc=code,
            coa=coa_model.__str__()
        ))


class AccountAssignmentsManager(models.Manager):

    def available(self):
        return self.get_queryset().filter(locked=False,
                                          active=True)

    def inactive(self):
        return self.get_queryset().filter(active=False)

    def active(self):
        return self.get_queryset().filter(active=True)

    def locked(self):
        return self.get_queryset().filter(locked=True)

    def unlocked(self):
        return self.get_queryset().filter(locked=False)


class CoAAccountAssignments(models.Model):
    # todo: add unique coa-acccode index.

    account = models.ForeignKey('django_ledger.AccountModel',
                                on_delete=models.CASCADE,
                                verbose_name='Accounts',
                                related_name='coa_assignments')

    coa = models.ForeignKey('django_ledger.ChartOfAccountModel',
                            on_delete=models.CASCADE,
                            verbose_name='Chart of Accounts',
                            related_name='acc_assignments')

    locked = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    objects = AccountAssignmentsManager()

    def __str__(self):
        return '{coa}: {acc}'.format(coa=self.coa.__str__(),
                                     acc=self.account.__str__()
                                     )

    class Meta:
        verbose_name = 'Chart of Account Assignment'


class ChartOfAccountModel(ChartOfAccountModelAbstract):
    """
    Final ChartOfAccountsModel from Abstracts
    """

    class Meta:
        verbose_name = 'Chart of Account'
