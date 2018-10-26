import books.models.io.preproc
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=5, unique=True)),
                ('parent', models.CharField(blank=True, max_length=5, null=True)),
                ('name', models.TextField()),
                ('role', models.CharField(choices=[('Assets', (('ca', 'Current Asset'), ('lti', 'Long Term Investments'), ('ppe', 'Property Plant & Equipment'), ('ia', 'Intangible Assets'), ('aadj', 'Asset Adjustments'))), ('Liabilities', (('cl', 'Current Liabilities'), ('ltl', 'Long Term Liabilities'))), ('Equity', (('cap', 'Capital'), ('cadj', 'Capital Adjustments'), ('in', 'Income'), ('ex', 'Expense'), ('capex', 'Capital Expenditure'))), ('Other', (('excl', 'Excluded'),))], max_length=10)),
                ('role_bs', models.CharField(max_length=20, null=True)),
                ('balance_type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit')], max_length=6)),
                ('locked', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChartOfAccountsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(max_length=20, unique=True)),
                ('coa', jsonfield.fields.JSONField(default={'1': {'acc_code': 1000, 'acc_name': 'CURRENT ASSETS', 'acc_parent': 1000, 'acc_role': 'ca', 'acc_type': 'debit'}, '10': {'acc_code': 1520, 'acc_name': 'Land', 'acc_parent': 1500, 'acc_role': 'lti', 'acc_type': 'debit'}, '100': {'acc_code': 7510, 'acc_name': 'Misc. Expense', 'acc_parent': 7500, 'acc_role': 'ex', 'acc_type': 'debit'}, '101': {'acc_code': 1640, 'acc_name': 'Vehicles', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'debit'}, '102': {'acc_code': 1640, 'acc_name': 'Less: Vehicles Accumulated Depreciation', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'credit'}, '103': {'acc_code': 1650, 'acc_name': 'Furniture & Fixtures', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'debit'}, '104': {'acc_code': 1651, 'acc_name': 'Less: Furniture & Fixtures Accumulated Depreciation', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'credit'}, '105': {'acc_code': 4030, 'acc_name': 'Property Sales Income', 'acc_parent': 4000, 'acc_role': 'in', 'acc_type': 'credit'}, '106': {'acc_code': 3920, 'acc_name': 'PPE Unrealized Gains/Losses', 'acc_parent': 3000, 'acc_role': 'cadj', 'acc_type': 'credit'}, '107': {'acc_code': 3910, 'acc_name': 'Available for Sale', 'acc_parent': 3000, 'acc_role': 'cadj', 'acc_type': 'credit'}, '11': {'acc_code': 1530, 'acc_name': 'Securities', 'acc_parent': 1500, 'acc_role': 'lti', 'acc_type': 'debit'}, '110': {'acc_code': 1800, 'acc_name': 'INTANGIBLE ASSETS', 'acc_parent': 1800, 'acc_role': 'ia', 'acc_type': 'debit'}, '111': {'acc_code': 1810, 'acc_name': 'Goodwill', 'acc_parent': 1800, 'acc_role': 'ia', 'acc_type': 'debit'}, '12': {'acc_code': 1600, 'acc_name': 'PPE', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'debit'}, '13': {'acc_code': 1610, 'acc_name': 'Buildings', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'debit'}, '14': {'acc_code': 1611, 'acc_name': 'Less: Buildings Accumulated Depreciation', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'credit'}, '15': {'acc_code': 1620, 'acc_name': 'Plant', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'debit'}, '16': {'acc_code': 1621, 'acc_name': 'Less: Plant Accumulated Depreciation', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'credit'}, '17': {'acc_code': 1630, 'acc_name': 'Equipment', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'debit'}, '18': {'acc_code': 1631, 'acc_name': 'Less: Equipment Accumulated Depreciation', 'acc_parent': 1600, 'acc_role': 'ppe', 'acc_type': 'credit'}, '19': {'acc_code': 1900, 'acc_name': 'ADJUSTMENTS', 'acc_parent': 1900, 'acc_role': 'aadj', 'acc_type': 'debit'}, '2': {'acc_code': 1010, 'acc_name': 'Cash', 'acc_parent': 1000, 'acc_role': 'ca', 'acc_type': 'debit'}, '20': {'acc_code': 1910, 'acc_name': 'Securities Unrealized Gains/Losses', 'acc_parent': 1900, 'acc_role': 'aadj', 'acc_type': 'debit'}, '21': {'acc_code': 1920, 'acc_name': 'PPE Unrealized Gains/Losses', 'acc_parent': 1900, 'acc_role': 'aadj', 'acc_type': 'debit'}, '23': {'acc_code': 2000, 'acc_name': 'CURRENT LIABILITIES', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '24': {'acc_code': 2010, 'acc_name': 'Current Liabilities', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '25': {'acc_code': 2020, 'acc_name': 'Wages Payable', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '26': {'acc_code': 2030, 'acc_name': 'Interest Payable', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '27': {'acc_code': 2040, 'acc_name': 'Short-Term Payable', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '28': {'acc_code': 2050, 'acc_name': 'Current Maturities LT Debt', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '29': {'acc_code': 2060, 'acc_name': 'Deferred Revenues', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '3': {'acc_code': 1050, 'acc_name': 'Short Term Investments', 'acc_parent': 1000, 'acc_role': 'ca', 'acc_type': 'debit'}, '30': {'acc_code': 2070, 'acc_name': 'Other Payables', 'acc_parent': 2000, 'acc_role': 'cl', 'acc_type': 'credit'}, '31': {'acc_code': 2100, 'acc_name': 'LONG TERM LIABILITIES', 'acc_parent': 2100, 'acc_role': 'ltl', 'acc_type': 'credit'}, '32': {'acc_code': 2110, 'acc_name': 'Long Term Notes Payable', 'acc_parent': 2100, 'acc_role': 'ltl', 'acc_type': 'credit'}, '33': {'acc_code': 2120, 'acc_name': 'Bonds Payable', 'acc_parent': 2100, 'acc_role': 'ltl', 'acc_type': 'credit'}, '34': {'acc_code': 2130, 'acc_name': 'Mortgage Payable', 'acc_parent': 2100, 'acc_role': 'ltl', 'acc_type': 'credit'}, '35': {'acc_code': 3000, 'acc_name': 'CAPITAL ACCOUNTS', 'acc_parent': 3000, 'acc_role': 'cap', 'acc_type': 'credit'}, '36': {'acc_code': 3010, 'acc_name': 'Capital Account 1', 'acc_parent': 3000, 'acc_role': 'cap', 'acc_type': 'credit'}, '37': {'acc_code': 3020, 'acc_name': 'Capital Account 2', 'acc_parent': 3000, 'acc_role': 'cap', 'acc_type': 'credit'}, '38': {'acc_code': 3030, 'acc_name': 'Capital Account 3', 'acc_parent': 3000, 'acc_role': 'cap', 'acc_type': 'credit'}, '39': {'acc_code': 4000, 'acc_name': 'REVENUE ACCOUNTS', 'acc_parent': 4000, 'acc_role': 'in', 'acc_type': 'credit'}, '4': {'acc_code': 1100, 'acc_name': 'Accounts Receivable', 'acc_parent': 1000, 'acc_role': 'ca', 'acc_type': 'debit'}, '40': {'acc_code': 4010, 'acc_name': 'Sales Income', 'acc_parent': 4000, 'acc_role': 'in', 'acc_type': 'credit'}, '41': {'acc_code': 4020, 'acc_name': 'Rental Income', 'acc_parent': 4000, 'acc_role': 'in', 'acc_type': 'credit'}, '42': {'acc_code': 5000, 'acc_name': 'COGS ACCOUNTS', 'acc_parent': 5000, 'acc_role': 'ex', 'acc_type': 'debit'}, '43': {'acc_code': 5010, 'acc_name': 'Cost of Goods Sold', 'acc_parent': 5000, 'acc_role': 'ex', 'acc_type': 'debit'}, '44': {'acc_code': 6000, 'acc_name': 'EXPENSE ACCOUNTS', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '45': {'acc_code': 6010, 'acc_name': 'Advertising', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '46': {'acc_code': 6020, 'acc_name': 'Amortization', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '47': {'acc_code': 6030, 'acc_name': 'Auto Expense', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '48': {'acc_code': 6040, 'acc_name': 'Bad Debt', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '49': {'acc_code': 6050, 'acc_name': 'Bank Charges', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '5': {'acc_code': 1101, 'acc_name': 'Uncollectibles', 'acc_parent': 1100, 'acc_role': 'ca', 'acc_type': 'credit'}, '50': {'acc_code': 6060, 'acc_name': 'Commission Expense', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '51': {'acc_code': 6070, 'acc_name': 'Depreciation Expense', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '52': {'acc_code': 6080, 'acc_name': 'Employee Benefits', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '53': {'acc_code': 6090, 'acc_name': 'Freight', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '54': {'acc_code': 6110, 'acc_name': 'Gifts', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '55': {'acc_code': 6120, 'acc_name': 'Insurance', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '56': {'acc_code': 6130, 'acc_name': 'Interest Expense', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '57': {'acc_code': 6140, 'acc_name': 'Professional Fees', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '58': {'acc_code': 6150, 'acc_name': 'License Expense', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '59': {'acc_code': 6170, 'acc_name': 'Maintenance Expense', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '6': {'acc_code': 1200, 'acc_name': 'Inventory', 'acc_parent': 1000, 'acc_role': 'ca', 'acc_type': 'debit'}, '60': {'acc_code': 6180, 'acc_name': 'Meals & Entertainment', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '61': {'acc_code': 6190, 'acc_name': 'Office Expense', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '62': {'acc_code': 6210, 'acc_name': 'Payroll Taxes', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '63': {'acc_code': 6220, 'acc_name': 'Printing', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '64': {'acc_code': 6230, 'acc_name': 'Postage', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '65': {'acc_code': 6240, 'acc_name': 'Rent', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '66': {'acc_code': 6250, 'acc_name': 'Maintenance & Repairs', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '67': {'acc_code': 6251, 'acc_name': 'Maintenance', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '68': {'acc_code': 6252, 'acc_name': 'Repairs', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '69': {'acc_code': 6253, 'acc_name': 'HOA', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '7': {'acc_code': 1300, 'acc_name': 'Prepaid Expenses', 'acc_parent': 1000, 'acc_role': 'ca', 'acc_type': 'debit'}, '70': {'acc_code': 6254, 'acc_name': 'Snow Removal', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '71': {'acc_code': 6255, 'acc_name': 'Lawn Care', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '72': {'acc_code': 6260, 'acc_name': 'Salaries', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '73': {'acc_code': 6270, 'acc_name': 'Supplies', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '74': {'acc_code': 6280, 'acc_name': 'Taxes', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '75': {'acc_code': 6290, 'acc_name': 'Utilities', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '77': {'acc_code': 6292, 'acc_name': 'Sewer', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '78': {'acc_code': 6293, 'acc_name': 'Gas', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '79': {'acc_code': 6294, 'acc_name': 'Garbage', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '8': {'acc_code': 1500, 'acc_name': 'LONG TERM INVESTMENTS', 'acc_parent': 1500, 'acc_role': 'lti', 'acc_type': 'debit'}, '80': {'acc_code': 6295, 'acc_name': 'Electricity', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '81': {'acc_code': 6300, 'acc_name': 'Property Management', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '82': {'acc_code': 6400, 'acc_name': 'Vacancy', 'acc_parent': 6000, 'acc_role': 'ex', 'acc_type': 'debit'}, '84': {'acc_code': 6901, 'acc_name': 'Roof', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '85': {'acc_code': 6902, 'acc_name': 'Water Heater', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '86': {'acc_code': 6903, 'acc_name': 'Appliances', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '87': {'acc_code': 6904, 'acc_name': 'Driveway & Parking', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '88': {'acc_code': 6905, 'acc_name': 'HVAC', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '89': {'acc_code': 6906, 'acc_name': 'Floring', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '9': {'acc_code': 1510, 'acc_name': 'Notes Receivable', 'acc_parent': 1500, 'acc_role': 'lti', 'acc_type': 'debit'}, '90': {'acc_code': 6907, 'acc_name': 'Plumbing', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '91': {'acc_code': 6908, 'acc_name': 'Windows', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '92': {'acc_code': 6909, 'acc_name': 'Paint', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '93': {'acc_code': 6910, 'acc_name': 'Cabinets & Counters', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '94': {'acc_code': 6911, 'acc_name': 'Structure', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '95': {'acc_code': 6912, 'acc_name': 'Components', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '96': {'acc_code': 6913, 'acc_name': 'Landscaping', 'acc_parent': 6000, 'acc_role': 'capex', 'acc_type': 'debit'}, '97': {'acc_code': 7000, 'acc_name': 'MISC. REVENUE ACCOUNTS', 'acc_parent': 7000, 'acc_role': 'in', 'acc_type': 'credit'}, '98': {'acc_code': 7010, 'acc_name': 'Misc. Revenue', 'acc_parent': 7000, 'acc_role': 'in', 'acc_type': 'credit'}, '99': {'acc_code': 7500, 'acc_name': 'MISC. EXPENSE ACCOUNTS', 'acc_parent': 7500, 'acc_role': 'ex', 'acc_type': 'debit'}})),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EntityModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_id', models.SlugField()),
                ('name', models.CharField(max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Entity',
                'verbose_name_plural': 'Entities',
            },
        ),
        migrations.CreateModel(
            name='JournalEntryModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('desc', models.CharField(blank=True, max_length=70, null=True)),
                ('freq', models.CharField(choices=[('nr', 'Non-Recurring'), ('d', 'Daily'), ('m', 'Monthly'), ('q', 'Quarterly'), ('y', 'Yearly'), ('sm', 'Monthly Series'), ('sy', 'Yearly Series')], max_length=2)),
                ('activity', models.CharField(choices=[('op', 'Operating'), ('fin', 'Financing'), ('inv', 'Investing'), ('other', 'Other')], max_length=5)),
                ('origin', models.CharField(blank=True, max_length=30, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LedgerModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('scope', models.CharField(choices=[('a', 'Actual'), ('f', 'Forecast'), ('b', 'Baseline')], max_length=1)),
                ('years_horizon', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.EntityModel')),
            ],
            options={
                'verbose_name': 'Ledger',
            },
            bases=(models.Model, books.models.io.preproc.IOPreProcMixIn, books.models.io.generic.IOGenericMixIn),
        ),
        migrations.CreateModel(
            name='TransactionModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tx_type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit')], max_length=10)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('params', jsonfield.fields.JSONField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='txs', to='books.AccountModel')),
                ('journal_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='txs', to='books.JournalEntryModel')),
            ],
        ),
        migrations.AddField(
            model_name='journalentrymodel',
            name='ledger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jes', to='books.LedgerModel'),
        ),
        migrations.AddField(
            model_name='journalentrymodel',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='books.JournalEntryModel'),
        ),
    ]
