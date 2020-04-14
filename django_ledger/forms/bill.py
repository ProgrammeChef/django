from django.forms import ModelForm, DateInput, TextInput, Select, EmailInput, URLInput
from django.forms import ValidationError

from django_ledger.forms import DJETLER_FORM_INPUT_CLASS
from django_ledger.io.roles import ASSET_CA_CASH, ASSET_CA_RECEIVABLES, LIABILITY_CL_ACC_PAYABLE, GROUP_INCOME
from django_ledger.models import BillModel, AccountModel


class BillModelCreateForm(ModelForm):

    def __init__(self, *args, entity_slug, user_model, **kwargs):
        super().__init__(*args, **kwargs)
        self.ENTITY_SLUG = entity_slug
        self.USER_MODEL = user_model
        account_qs = AccountModel.on_coa.for_entity(user_model=self.USER_MODEL,
                                                    entity_slug=self.ENTITY_SLUG)

        self.fields['cash_account'].queryset = account_qs.filter(role__exact=ASSET_CA_CASH)
        self.fields['receivable_account'].queryset = account_qs.filter(role__exact=ASSET_CA_RECEIVABLES)
        self.fields['payable_account'].queryset = account_qs.filter(role__exact=LIABILITY_CL_ACC_PAYABLE)
        self.fields['income_account'].queryset = account_qs.filter(role__in=GROUP_INCOME)

    class Meta:
        model = BillModel
        fields = [
            'xref',
            'date',
            'amount_due',
            'terms',
            'bill_to',
            'address_1',
            'address_2',
            'phone',
            'email',
            'website',
            'cash_account',
            'receivable_account',
            'payable_account',
            'income_account'
        ]
        widgets = {
            'date': DateInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'xref': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'amount_due': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'terms': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'bill_to': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'address_1': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'address_2': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'phone': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'email': EmailInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'website': URLInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'cash_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'receivable_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'payable_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'income_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
        }


class BillModelUpdateForm(ModelForm):

    def clean(self):
        amount_paid = self.cleaned_data.get('amount_paid')
        amount_due = self.cleaned_data.get('amount_due')
        if amount_paid > amount_due:
            raise ValidationError(
                'Amount paid cannot exceed bill amount due'
            )

    class Meta:
        model = BillModel
        fields = [
            'xref',
            'bill_to',
            'address_1',
            'address_2',
            'phone',
            'email',
            'website',
            'date',
            'terms',
            'amount_due',
            'amount_paid',
            'paid',
            'paid_date',
            'progress',
            'progressible'
        ]
        widgets = {
            'xref': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'bill_to': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'address_1': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'address_2': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'phone': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'email': EmailInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'website': URLInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),

            'date': DateInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'paid_date': DateInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'amount_due': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'amount_paid': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'terms': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),

            'progress': TextInput(attrs={'class': DJETLER_FORM_INPUT_CLASS}),

            'cash_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'receivable_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'payable_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
            'income_account': Select(attrs={'class': DJETLER_FORM_INPUT_CLASS}),
        }
