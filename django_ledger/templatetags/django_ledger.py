from datetime import datetime

from django import template

from django_ledger.forms import EntityModelDefaultForm, AsOfDateForm
from django_ledger.models.utils import get_date_filter_session_key, get_default_entity_session_key
from django_ledger.models_abstracts.journal_entry import validate_activity

register = template.Library()


@register.filter(name='cs_thousands')
def cs_thousands(value):
    return '{:,}'.format(value)


@register.inclusion_tag('django_ledger/tags/balance_sheet.html', takes_context=True)
def balance_sheet(context, entity_model):
    activity = context['request'].GET.get('activity')
    activity = validate_activity(activity, raise_404=True)
    return entity_model.snapshot(activity=activity)


@register.inclusion_tag('django_ledger/tags/income_statement.html', takes_context=True)
def income_statement(context, entity_model):
    activity = context['view'].kwargs.get('activity')
    ic_data = entity_model.income_statement(signs=True, activity=activity)
    income = [acc for acc in ic_data if acc['role'] in ['in']]
    expenses = [acc for acc in ic_data if acc['role'] in ['ex']]
    for ex in expenses:
        ex['balance'] = -ex['balance']
    total_income = sum([acc['balance'] for acc in income])
    total_expenses = sum([acc['balance'] for acc in expenses])
    total_income_loss = total_income - total_expenses

    return {
        'ic_data': ic_data,
        'income': income,
        'total_income': total_income,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'total_income_loss': total_income_loss
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
    session_key = get_default_entity_session_key()
    default_entity_id = context['request'].session.get(session_key)
    default_entity_form = EntityModelDefaultForm(user_model=user,
                                                 default_entity=default_entity_id)
    return {
        'default_entity_form': default_entity_form
    }


@register.inclusion_tag('django_ledger/tags/breadcrumbs.html', takes_context=True)
def nav_breadcrumbs(context):
    entity_slug = context['view'].kwargs.get('entity_slug')
    coa_slug = context['view'].kwargs.get('coa_slug')
    ledger_pk = context['view'].kwargs.get('entity_slug')
    account_pk = context['view'].kwargs.get('account_pk')
    return {
        'entity_slug': entity_slug,
        'coa_slug': coa_slug,
        'ledger_pk': ledger_pk,
        'account_pk': account_pk
    }


@register.inclusion_tag('django_ledger/tags/date_form.html', takes_context=True)
def date_filter_form(context):
    entity_slug = context['view'].kwargs.get('entity_slug')
    if entity_slug:
        form = AsOfDateForm(initial={
            'entity_slug': context['view'].kwargs['entity_slug']
        })
        next_url = context['request'].path
        return {
            'date_form': form,
            'entity_slug': entity_slug,
            'next': next_url
        }


@register.simple_tag(takes_context=True)
def current_entity_date(context):
    entity_slug = context['view'].kwargs.get('entity_slug')
    session_item = get_date_filter_session_key(entity_slug)
    session = context['request'].session
    date_filter = session.get(session_item)
    if not date_filter:
        date_filter = datetime.now().date().strftime('%Y-%m-%d')
        session[session_item] = date_filter
    return date_filter
