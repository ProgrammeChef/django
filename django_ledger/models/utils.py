from django.contrib.auth import get_user_model

from django_ledger.models.accounts import AccountModel
from django_ledger.models.coa_default import CHART_OF_ACCOUNTS
from django_ledger.models.entity import EntityModel
from django_ledger.models_abstracts.accounts import BS_ROLES, ACCOUNT_TERRITORY

UserModel = get_user_model()


def txs_digest(tx: dict) -> dict:
    tx['role_bs'] = BS_ROLES.get(tx['account__role'])
    if tx['account__balance_type'] != tx['tx_type']:
        tx['amount'] = -tx['amount']
    if tx['account__balance_type'] != ACCOUNT_TERRITORY.get(tx['role_bs']):
        tx['amount'] = -tx['amount']
    return tx


def populate_default_coa(entity_model: EntityModel):
    acc_objs = [AccountModel(
        code=a['code'],
        name=a['name'],
        role=a['role'],
        balance_type=a['balance_type'],
        coa=entity_model.coa,
    ) for a in CHART_OF_ACCOUNTS]
    parents = set([a.get('parent') for a in CHART_OF_ACCOUNTS])
    children = {
        p: [c['code']
            for c in CHART_OF_ACCOUNTS if c['parent'] == p and c['code'] != p] for p in parents
    }

    acc_children = list()
    for parent, child_list in children.items():
        parent_model = next(iter([a for a in acc_objs if a.code == parent]))
        parent_model.full_clean()
        parent_model.insert_at(target=None, save=True)

        for child in child_list:
            child_model = next(iter([acc for acc in acc_objs if acc.code == child]))
            child_model.full_clean()
            child_model.insert_at(target=parent_model, save=False)
            acc_children.append(child_model)
    AccountModel.objects.bulk_create(acc_children)


def make_accounts_active(entity_model: EntityModel, account_code_set: set):
    accounts = entity_model.coa.accounts.filter(code__in=account_code_set)
    accounts.update(active=True)
