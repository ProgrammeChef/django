from collections import namedtuple
from datetime import datetime
from typing import List, Set

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum

from django_ledger.abstracts.journal_entry import validate_activity
from django_ledger.io import roles
from django_ledger.io.ratios import FinancialRatioManager
from django_ledger.io.roles import RolesManager
from django_ledger.models.journalentry import JournalEntryModel

UserModel = get_user_model()


class LazyImporter:
    """
    This class eliminates the circle dependency between models.
    """
    ENTITY_MODEL = None
    LEDGER_MODEL = None
    TXS_MODEL = None

    def get_entity_model(self):
        if not self.ENTITY_MODEL:
            from django_ledger.models.entity import EntityModel
            self.ENTITY_MODEL = EntityModel
        return self.ENTITY_MODEL

    def get_txs_model(self):
        if not self.TXS_MODEL:
            from django_ledger.models.transactions import TransactionModel
            self.TXS_MODEL = TransactionModel
        return self.TXS_MODEL

    def get_ledger_model(self):
        if not self.LEDGER_MODEL:
            from django_ledger.models.ledger import LedgerModel
            self.LEDGER_MODEL = LedgerModel
        return self.LEDGER_MODEL


lazy_importer = LazyImporter()

AccountIndexTuple = namedtuple('AccountIndexTuple',
                               field_names='account_id, role_bs, role, code, name, balance_type, balance')


def validate_tx_data(tx_data: list):
    credits = sum(tx['amount'] for tx in tx_data if tx['tx_type'] == 'credit')
    debits = sum(tx['amount'] for tx in tx_data if tx['tx_type'] == 'debit')
    if not credits == debits:
        raise ValidationError(f'Invalid tx data. Credits and debits must match. Currently cr: {credits}, db {debits}.')
    return tx_data


class IOMixIn:
    """
    Controls how transactions are recorded into the ledger.
    """

    TX_DATA = None
    TX_DIGEST = None

    def create_je_acc_id(self,
                         je_date: str or datetime,
                         je_txs: list,
                         je_activity: str,
                         je_posted: bool = False,
                         je_ledger=None,
                         je_desc=None,
                         je_origin=None,
                         je_parent=None):

        # Validates that credits/debits balance.
        je_txs = validate_tx_data(je_txs)

        # Validates that the activity is valid.
        je_activity = validate_activity(je_activity)

        if all([isinstance(self, lazy_importer.get_entity_model()),
                not je_ledger]):
            raise ValidationError('Must pass an instance of LedgerModel')

        if not je_ledger:
            je_ledger = self

        je = JournalEntryModel.objects.create(
            ledger=je_ledger,
            description=je_desc,
            date=je_date,
            origin=je_origin,
            activity=je_activity,
            posted=je_posted,
            parent=je_parent
        )

        TransactionModel = lazy_importer.get_txs_model()
        txs_list = [
            TransactionModel(
                account_id=tx['account_id'],
                tx_type=tx['tx_type'],
                amount=tx['amount'],
                description=tx['description'],
                journal_entry=je
            ) for tx in je_txs
        ]
        txs = TransactionModel.objects.bulk_create(txs_list)
        return txs

    def create_je(self,
                  je_date: str or datetime,
                  je_txs: list,
                  je_activity: str,
                  je_posted: bool = False,
                  je_ledger=None,
                  je_desc=None,
                  je_origin=None,
                  je_parent=None):

        # Validates that credits/debits balance.
        je_txs = validate_tx_data(je_txs)

        # Validates that the activity is valid.
        je_activity = validate_activity(je_activity)

        # todo: revisit & remove unused TxS Model Querysets.
        if all([isinstance(self, lazy_importer.get_entity_model()),
                not je_ledger]):
            raise ValidationError('Must pass an instance of LedgerModel')

        if not je_ledger:
            je_ledger = self

        txs_accounts = [acc['code'] for acc in je_txs]

        if isinstance(self, lazy_importer.get_entity_model()):
            account_models = self.coa.accounts.all()
        elif isinstance(self, lazy_importer.get_ledger_model()):
            account_models = self.entity.coa.accounts.all()
        else:
            account_models = self.coa.accounts.none()

        avail_accounts = account_models.filter(code__in=txs_accounts)

        je = JournalEntryModel.objects.create(
            ledger=je_ledger,
            description=je_desc,
            date=je_date,
            origin=je_origin,
            activity=je_activity,
            posted=je_posted,
            parent=je_parent)

        TransactionModel = lazy_importer.get_txs_model()
        txs_list = [
            TransactionModel(
                account=avail_accounts.get(code__iexact=tx['code']),
                tx_type=tx['tx_type'],
                amount=tx['amount'],
                description=tx['description'],
                journal_entry=je
            ) for tx in je_txs
        ]
        txs = TransactionModel.objects.bulk_create(txs_list)
        return txs

    def get_je_txs(self,
                   user_model: UserModel,
                   as_of: str or datetime = None,
                   activity: str = None,
                   role: str = None,
                   accounts: str or List[str] or Set[str] = None,
                   posted: bool = True,
                   exclude_zero_bal: bool = True):

        activity = validate_activity(activity)
        role = roles.validate_roles(role)

        TransactionModel = lazy_importer.get_txs_model()
        if isinstance(self, lazy_importer.get_entity_model()):
            # Is entity model....
            txs = TransactionModel.objects.for_entity(entity_slug=self)
        elif isinstance(self, lazy_importer.get_ledger_model()):
            # Is ledger model ...
            txs = TransactionModel.objects.for_ledger(ledger_model=self)
        else:
            txs = TransactionModel.objects.none()

        # Make sure transa
        txs = txs.for_user(user_model=user_model)

        if exclude_zero_bal:
            txs = txs.filter(amount__gt=0)

        if posted:
            txs = txs.posted()

        if as_of:
            txs = txs.as_of(as_of_date=as_of)

        if accounts:
            if not isinstance(accounts, str):
                accounts = [accounts]
            txs = txs.for_accounts(account_list=accounts)

        if activity:
            if isinstance(activity, str):
                activity = [activity]
            txs = txs.for_activity(activity_list=activity)
        if role:
            if isinstance(role, str):
                role = [role]
            txs = txs.for_roles(role_list=role)

        txs = txs.values(
            'account__id',
            'account__balance_type',
            'tx_type',
            'account__code',
            'account__name',
            'account__role',
        ).annotate(balance=Sum('amount')).order_by('account__code')
        return txs

    def get_jes(self,
                user: UserModel,
                as_of: str = None,
                equity_only: bool = False,
                activity: str = None,
                role: str = None,
                accounts: set = None,
                signs: bool = False):

        if equity_only:
            role = roles.GROUP_EARNINGS

        je_txs = self.get_je_txs(
            user_model=user,
            as_of=as_of,
            activity=activity,
            role=role,
            accounts=accounts)

        # reverts the amount sign if the tx_type does not math the account_type.
        for tx in je_txs:
            if tx['account__balance_type'] != tx['tx_type']:
                tx['balance'] = -tx['balance']

        acc_balances = set(AccountIndexTuple(
            account_id=je['account__id'],
            role_bs=roles.BS_ROLES.get(je['account__role']),
            role=je['account__role'],
            code=je['account__code'],
            name=je['account__name'],
            balance_type=je['account__balance_type'],
            balance=sum(r['balance'] for r in je_txs if r['account__code'] == je['account__code'])
        ) for je in je_txs)
        acc_balances = [acc_idx._asdict() for acc_idx in acc_balances]

        if signs:
            for acc in acc_balances:
                if any([
                    all([acc['role_bs'] == 'assets',
                         acc['balance_type'] == 'credit']),
                    all([acc['role_bs'] in ('liabilities', 'equity', 'other'),
                         acc['balance_type'] == 'debit'])
                ]):
                    acc['balance'] = -acc['balance']

        return acc_balances

    def digest(self,
               user_model: UserModel,
               accounts: set = None,
               activity: str = None,
               as_of: str = None,
               process_roles: bool = True,
               process_groups: bool = False,
               process_ratios: bool = False,
               equity_only: bool = False) -> dict:

        accounts = self.get_jes(signs=True,
                                user=user_model,
                                accounts=accounts,
                                activity=activity,
                                as_of=as_of,
                                equity_only=equity_only)

        digest = dict(
            accounts=accounts
        )

        roles_mgr = RolesManager(tx_digest=digest, roles=process_roles, groups=process_groups)
        digest = roles_mgr.generate()

        if process_ratios:
            ratio_gen = FinancialRatioManager(tx_digest=digest)
            digest = ratio_gen.generate()

        return {
            'tx_digest': digest,
        }
