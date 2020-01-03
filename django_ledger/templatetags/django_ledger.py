from django import template

from django_ledger.forms import EntityModelDefaultForm

register = template.Library()


@register.filter(name='cs_thousands')
def cs_thousands(value):
    return '{:,}'.format(value)


@register.inclusion_tag('django_ledger/tags/balance_sheet.html')
def balance_sheet(entity_model):
    return entity_model.snapshot()


@register.inclusion_tag('django_ledger/tags/income_statement.html')
def income_statement(entity_model):
    ic_data = entity_model.income_statement()
    income = [acc for acc in ic_data if acc['role'] in ['in']]
    expenses = [acc for acc in ic_data if acc['role'] in ['ex']]
    total_income = sum(
        [acc['balance'] for acc in income if acc['balance_type'] == 'credit'] +
        [-acc['balance'] for acc in income if acc['balance_type'] == 'debit'])
    total_expenses = -sum(
        [acc['balance'] for acc in expenses if acc['balance_type'] == 'credit'] +
        [-acc['balance'] for acc in expenses if acc['balance_type'] == 'debit'])

    return {
        'ic_data': ic_data,
        'income': income,
        'total_income': total_income,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'total_income_loss': total_income - total_expenses
    }


@register.inclusion_tag('django_ledger/tags/jes_table.html', takes_context=True)
def jes_table(context, je_queryset):
    return {
        'jes': je_queryset,
        'entity_slug': context['view'].kwargs['entity_slug']
    }


@register.inclusion_tag('django_ledger/tags/txs_table.html')
def txs_table(je_model):
    txs_queryset = je_model.txs.all()
    total_credits = sum([tx.amount for tx in txs_queryset if tx.tx_type == 'credit'])
    total_debits = sum([tx.amount for tx in txs_queryset if tx.tx_type == 'debit'])
    return {
        'txs': txs_queryset,
        'total_debits': total_debits,
        'total_credits': total_credits
    }


@register.inclusion_tag('django_ledger/tags/ledgers_table.html', takes_context=True)
def ledgers_table(context, ledgers_queryset):
    return {
        'ledgers': ledgers_queryset,
        'entity_slug': context['view'].kwargs['entity_slug']
    }


@register.inclusion_tag('django_ledger/tags/accounts_table.html')
def accounts_table(accounts_queryset):
    return {
        'accounts': accounts_queryset
    }


@register.inclusion_tag('django_ledger/tags/default_entity_form.html', takes_context=True)
def entity_choice_form(context):
    user = context['user']
    default_entity_id = context['request'].session.get('default_entity_id')
    default_entity_form = EntityModelDefaultForm(user_model=user,
                                                 default_entity=default_entity_id)
    return {
        'default_entity_form': default_entity_form
    }
