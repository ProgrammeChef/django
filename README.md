# Django Ledger

### A bookkeeping & financial analysis app for the Django Framework.

Django Ledger supports:

- Chart of Accounts.
- Financial Statements (Income Statement & Balance Sheets)
- Entities (LLC, Corps, etc.)
- General Ledgers
- Journal Entries & Transactions.
- Recurring transactions.

Currently this project is under active development and is not recommended for production environments.
The author is working on incorporating the following functionality:

- Multiple debit/credit operations with transactions.
- Internationalization.
- Views & template tags.
___

## Quick Start

In order to start using Django Ledger you must create a Chart of Accounts (CoA).
Django Ledger comes with a default CoA ready to use or you could use your own.

```python
from django_ledger.models.accounts import AccountModel
from django_ledger.models.coa import ChartOfAccountModel, make_account_active, get_acc_idx
from django_ledger.models.coa_default import CHART_OF_ACCOUNTS
from django_ledger.models.entity import EntityModel
from django_ledger.models.utils import create_coa_structure

# USE WITH CAUTION!!!!, WILL DELETE ENTIRE DATABASE.
RESET_DATABASE = False

if RESET_DATABASE:
    EntityModel.objects.all().delete()
    ChartOfAccountModel.objects.all().delete()
    AccountModel.objects.all().delete()
    coa = create_coa_structure(coa_data=CHART_OF_ACCOUNTS, coa_name='CoA QuickStart')
    make_account_active(coa, ['1010', '3010', '1610', '2110', '6253', '4020'])

coa, created = ChartOfAccountModel.objects.get_or_create(name='CoA QuickStart')

company, created = EntityModel.objects.get_or_create(slug='my-co-inc',
                                                     coa=coa,
                                                     name='MyCo Inc')

ledger_id = 'my-co-ledger'  # auto generated if not provided
myco_ledger, created = company.general_ledger.get_or_create(slug=ledger_id, name='My Debug Ledger')

myco_ledger.journal_entry.all().delete()

# Company Funding
funding = 200000
myco_ledger.tx_generic(
    amount=funding,
    start_date='2019-10-02',
    debit_acc='1010',
    credit_acc='3010',
    activity='other',
    desc='Company funding.'
)

# Buy property
myco_ledger.tx_generic(
    amount=40000,
    start_date='2019-10-02',
    debit_acc='1610',
    credit_acc='1010',
    activity='inv',
    desc='Real estate down payment'
)

# Funding Company ---
myco_ledger.tx_generic(
    amount=80000,
    start_date='2019-10-02',
    debit_acc='1610',
    credit_acc='2110',
    activity='fin',
    desc='Mortgage to buy real estate.'
)

# An expense ----
myco_ledger.tx_generic(
    amount=100,
    start_date='2019-11-02',
    debit_acc='6253',
    credit_acc='1010',
    activity='op',
    desc='HOA Expenses Nov 2019'
)

# An Income ----
myco_ledger.tx_generic(
    amount=1200,
    start_date='2019-11-06',
    debit_acc='1010',
    credit_acc='4020',
    activity='op',
    desc='HOA Expenses Nov 2019'
)

# Balance Sheet & Income Statement, optional as pandas DataFrame parameter ----
bs = myco_ledger.balance_sheet(as_dataframe=True, signs=0)
ic = myco_ledger.income_statement(as_dataframe=True, signs=True)

```


__Want to contribute? Don't hesitate to contact me.__