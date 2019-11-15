from random import randint

import pandas as pd
from django.db import models
from django.db.models.signals import post_init, pre_save
from django.utils.text import slugify
from django_pandas.io import read_frame
from pandas.tseries.offsets import MonthEnd

from django_ledger.models.accounts import validate_roles
from django_ledger.models.coa import get_coa_account, get_acc_idx
from django_ledger.models.io.generic import IOGenericMixIn
from django_ledger.models.io.preproc import IOPreProcMixIn
from django_ledger.models.journalentry import validate_activity
from django_ledger.models.mixins import CreateUpdateMixIn, SlugNameMixIn
from django_ledger.models.transactions import TransactionModel

COA_ATTR = 'coa_model'


def get_ledger_coa(ledger_model):
    """
    Utility function to get the associated ledger's Chart of Account model.
    :param ledger_model: A Ledger model instance
    :return:
    """
    return ledger_model.entity.coa


def process_signs(row):
    idx = [x.lower() for x in row.name]
    if 'assets' in idx and 'credit' in idx:
        row = -row
    if ('liabilities' in idx or 'equity' in idx or 'other' in idx) and 'debit' in idx:
        row = -row
    return row


class LedgerModelManager(models.Manager):

    def posted(self):
        return self.get_queryset().filter(posted=True)


class LedgerModelAbstract(SlugNameMixIn,
                          CreateUpdateMixIn,
                          IOPreProcMixIn,
                          IOGenericMixIn):
    posted = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    entity = models.ForeignKey('django_ledger.EntityModel',
                               on_delete=models.CASCADE,
                               related_name='general_ledger')

    objects = LedgerModelManager()

    class Meta:
        abstract = True

    def __str__(self):
        return '{slug}: {name}'.format(name=self.name,
                                       slug=self.slug)

    def get_coa(self):
        return getattr(self, COA_ATTR)

    # TODO: This can be handled by the Model Manager...?
    def get_accounts(self, status='available'):
        choices = (
            'available',
            'inactive',
            'active',
            'locked',
            'unlocked'
        )
        if status not in choices:
            raise ValueError('Invalid account status.')
        coa = self.get_coa()
        return getattr(coa.acc_assignments, status)()

    def get_account(self, code):
        """
        Convenience method to get an account model instance from the ledger entity Chart of Accounts.
        :param code: Account code.
        :return:
        """
        return get_coa_account(coa_model=self.get_coa(),
                               code=code)

    def get_jes_data(self, as_dataframe=False):
        jes = list(self.jes.all().values())
        if as_dataframe:
            jes = pd.DataFrame(jes)
            jes.rename(columns={'id': 'je_id'}, inplace=True)
            jes.set_index('je_id', inplace=True)
            jes['start_date'] = pd.to_datetime(jes['start_date'])
            jes['end_date'] = pd.to_datetime(jes['end_date'])
        return jes

    def get_tx_data(self, as_dataframe=False):
        tx = TransactionModel.objects.filter(journal_entry__ledger__exact=self)
        tx = list(tx.values())
        if as_dataframe:
            tx = pd.DataFrame(tx)
            tx.rename(columns={'id': 'tx_id'}, inplace=True)
            tx.set_index('tx_id', inplace=True)
        return tx

    def get_jes_tx_df(self, as_dataframe=False, activity=None, role=None, account=None):

        """
        If account is present all other parameters will be ignored.

        :param as_dataframe:
        :param activity:
        :param role:
        :param account:
        :return:
        """
        activity = validate_activity(activity)
        role = validate_roles(role)

        jes = self.journal_entry.filter(ledger__exact=self)

        if account:
            if isinstance(account, str) or isinstance(account, int):
                account = [account]
            jes = self.journal_entry.filter(txs__account__code__in=account)
        if activity:
            if isinstance(activity, str):
                activity = [activity]
            jes = jes.filter(activity__in=activity)
        if role:
            if isinstance(role, str):
                role = [role]
            jes = jes.filter(txs__account__role__in=role)

        jes_tx_df = read_frame(jes, fieldnames=['id', 'origin', 'freq', 'start_date', 'end_date', 'activity',
                                                'txs__id', 'txs__tx_type',
                                                'txs__account__code',
                                                'txs__account__name',
                                                'txs__account__balance_type',
                                                'txs__account__role',
                                                'txs__amount', 'txs__params'],
                               verbose=False)

        jes_tx_df.rename(columns={'id': 'je_id',
                                  'txs__id': 'tx_id',
                                  'txs__tx_type': 'tx_type',
                                  'txs__account': 'account',
                                  'txs__account__code': 'code',
                                  'txs__account__name': 'name',
                                  'txs__account__balance_type': 'balance_type',
                                  'txs__account__role': 'role',
                                  'txs__amount': 'amount',
                                  'txs__params': 'params'},
                         inplace=True)

        jes_tx_df.set_index(keys=['je_id', 'tx_id'], inplace=True)
        jes_tx_df['start_date'] = pd.to_datetime(jes_tx_df['start_date'])
        jes_tx_df['end_date'] = pd.to_datetime(jes_tx_df['end_date'])

        pe_start = pd.to_datetime(jes_tx_df['start_date'], format="%Y%m") + MonthEnd(0)
        jes_tx_df['pe_start'] = pe_start

        pe_finish = pd.to_datetime(jes_tx_df['end_date'], format="%Y%m") + MonthEnd(0)
        jes_tx_df['pe_finish'] = pe_finish

        def sm_pe(row):
            if row['freq'][0] == 's':
                row['pe_finish'] = row['pe_finish'] - pd.DateOffset(months=1) + MonthEnd(0)
            return row

        jes_tx_df = jes_tx_df.apply(func=sm_pe, axis=1)

        if not as_dataframe:
            jes_tx_df = jes_tx_df.reset_index().to_dict(orient='records')

        return jes_tx_df

    def get_ts_df(self, cum=True, as_dataframe=False, method='bs', activity=None, role=None, account=None):

        if method == 'ic':
            role = ['in', 'ex']
        elif method == 'ic-op':
            role = ['in', 'ex']
            activity = ['op']
        elif method == 'ic-inv':
            role = ['in', 'ex']
            activity = ['inv']
        elif method == 'ic-fin':
            role = ['in', 'ex']
            activity = ['fin']

        je_txs = self.get_jes_tx_df(activity=activity,
                                    role=role,
                                    account=account,
                                    as_dataframe=True)

        if not je_txs.empty:

            # Comment: Looking for the min & max dates of all JE's & transactions for index.
            i_start = je_txs[['pe_start', 'pe_finish']].min().min().date()
            i_finish = je_txs[['pe_start', 'pe_finish']].max().max().date()

            # Comment: If horizon for model, trim index.
            # if i_finish.year - i_start.year > self.years_horizon:
            #     i_finish = i_start + relativedelta(years=self.years_horizon)

            # Creating empty DF with the index.
            index = pd.date_range(start=i_start, end=i_finish, freq='m')
            df = pd.DataFrame(index=index)

            for row in je_txs.iterrows():
                freq = row[1]['freq']
                if freq == 'nr':
                    iter_index = pd.date_range(start=row[1]['pe_start'], end=row[1]['pe_start'], freq='m')
                elif freq[0] == 's':

                    if freq[1] == 'y':
                        offset = MonthEnd(12)
                        iter_index = pd.date_range(start=row[1]['pe_start'], end=row[1]['pe_finish'],
                                                      freq=offset)
                    else:
                        iter_index = pd.date_range(start=row[1]['pe_start'], end=row[1]['pe_finish'],
                                                      freq=row[1]['freq'][1])
                else:
                    iter_index = pd.date_range(start=row[1]['pe_start'], end=row[1]['pe_finish'],
                                                  freq=row[1]['freq'])

                idx_df = pd.DataFrame(index=iter_index)

                if row[1]['freq'][0] == 's':
                    amount = pd.DataFrame(eval(row[1]['params'])['series'], index=iter_index).iloc[:, 0]
                else:
                    amount = row[1]['amount']

                if row[1]['tx_type'] == row[1]['balance_type']:
                    idx_df[row[1]['code']] = pd.to_numeric(amount)
                else:
                    idx_df[row[1]['code']] = -pd.to_numeric(amount)

                df = pd.concat([df, idx_df], axis=1)

            df = df.transpose()
            df.index.rename('code', inplace=True)
            df = df.groupby('code').sum()

            df = pd.merge(left=get_acc_idx(
                coa_model=get_ledger_coa(self),
                as_dataframe=True
            ), right=df, how='inner', left_index=True, right_index=True)
            df.fillna(value=0, inplace=True)
            df.columns.name = 'period'

            if cum:
                df = df.cumsum(axis=1)

            if as_dataframe:
                return df
            else:
                df = df.stack()
                df.name = 'value'
                df = df.to_frame()
                return df.reset_index().to_dict(orient='records')

    # Financial Statements -----
    def balance_sheet(self, cum=True, signs=False, as_dataframe=False, activity=None):

        bs_df = self.get_ts_df(cum=cum,
                               activity=activity,
                               method='bs',
                               as_dataframe=True)

        if signs:
            bs_df = bs_df.apply(process_signs, axis=1)

        if not as_dataframe:
            bs_df = bs_df.stack()
            bs_df.name = 'value'
            bs_df = bs_df.reset_index().to_dict(orient='records')

        return bs_df

    def income_statement(self, cum=True, signs=False, as_dataframe=False, activity=None):

        method = 'ic'
        if isinstance(activity, str):
            method += '-{x1}'.format(x1=activity)

        ic_df = self.get_ts_df(cum=cum,
                               method=method,
                               as_dataframe=True)

        if signs:
            ic_df = ic_df.apply(process_signs, axis=1)

        if not as_dataframe:
            ic_df = ic_df.stack()
            ic_df.name = 'value'
            ic_df = ic_df.reset_index().to_dict(orient='records')

        return ic_df

    def income(self, activity=None):
        inc_df = self.income_statement(cum=False, signs=True, as_dataframe=False, activity=activity).sum()
        return inc_df

    # def acc_balance(self, acc_code, date):
    #     acc_code = str(acc_code)
    #     ts_df = self.get_ts_df().stack()
    #     ts_df.index.rename('timestamp', level=7, inplace=True)
    #     ts_df.name = 'balance'
    #     ts_df = ts_df.reset_index()[['acc_code', 'timestamp', 'balance']]
    #     ts_df.set_index(keys=['acc_code', 'timestamp'], inplace=True)
    #     balance = ts_df.loc[acc_code].loc[date]['balance'][-1]
    #     return balance

    def get_accout_balance(self, acc_code, period):
        return self.get_ts_df(account=acc_code).iloc[0][period].iloc[0]


class LedgerModel(LedgerModelAbstract):
    """
    Final LedgerModel from Abstracts
    """


def ledgermodel_postinit(sender, instance, **kwargs):
    coa = get_ledger_coa(instance)
    setattr(instance, COA_ATTR, coa)


post_init.connect(ledgermodel_postinit, LedgerModel)


def ledgermodel_presave(sender, instance, **kwargs):
    if not instance.slug:
        r_int = randint(10000, 99999)
        slug = slugify(instance.name)
        instance.slug = f'{slug}-{r_int}'
    print('Ledger {} Pre-Save...'.format(instance.slug))


pre_save.connect(ledgermodel_presave, LedgerModel)
