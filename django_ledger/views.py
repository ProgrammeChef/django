from django.db.models import Q
from django.db.models import Value, CharField
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, TemplateView

from django_ledger.forms import (AccountModelForm, AccountModelCreateForm, LedgerModelCreateForm, LedgerModelUpdateForm,
                                 JournalEntryModelForm, TransactionModelFormSet)
from django_ledger.models import (EntityModel, ChartOfAccountModel, TransactionModel,
                                  AccountModel, LedgerModel, JournalEntryModel)


class EntityModelListView(ListView):
    template_name = 'django_ledger/entities.html'
    context_object_name = 'entities'

    def get_queryset(self):
        """
        Returns a queryset of all Entities owned or Managed by the User.
        Queryset is annotated with user_role parameter (owned/managed).
        :return: The View queryset.
        """
        owned = EntityModel.objects.filter(
            admin=self.request.user).annotate(
            user_role=Value('owned', output_field=CharField())
        )
        managed = EntityModel.objects.filter(entity_permissions__user=self.request.user).annotate(
            user_role=Value('managed', output_field=CharField())
        )
        return owned.union(managed).distinct()


class EntityModelDetailVew(DetailView):
    context_object_name = 'entity'
    slug_url_kwarg = 'entity_slug'
    template_name = 'django_ledger/entity_detail.html'

    def get_queryset(self):
        """
        Returns a queryset of all Entities owned or Managed by the User.
        Queryset is annotated with user_role parameter (owned/managed).
        :return: The view queryset.
        """
        return EntityModel.objects.filter(
            Q(admin=self.request.user) |
            Q(entity_permissions__user=self.request.user)
        ).select_related('coa')


class EntityBalanceSheetView(DetailView):
    context_object_name = 'entity'
    slug_url_kwarg = 'entity_slug'
    template_name = 'django_ledger/balance_sheet.html'

    def get_queryset(self):
        """
        Returns a queryset of all Entities owned or Managed by the User.
        Queryset is annotated with user_role parameter (owned/managed).
        :return: The view queryset.
        """
        return EntityModel.objects.filter(
            Q(admin=self.request.user) |
            Q(entity_permissions__user=self.request.user)
        )


class EntityIncomeStatementView(DetailView):
    context_object_name = 'entity'
    slug_url_kwarg = 'entity_slug'
    template_name = 'django_ledger/income_statement.html'

    def get_queryset(self):
        """
        Returns a queryset of all Entities owned or Managed by the User.
        Queryset is annotated with user_role parameter (owned/managed).
        :return: The view queryset.
        """
        return EntityModel.objects.filter(
            Q(admin=self.request.user) |
            Q(entity_permissions__user=self.request.user)
        )


class ChartOfAccountsDetailView(DetailView):
    context_object_name = 'coa'
    slug_url_kwarg = 'coa_slug'
    template_name = 'django_ledger/coa_detail.html'

    def get_queryset(self):
        return ChartOfAccountModel.objects.filter(
            Q(user=self.request.user) |
            Q(entitymodel__entity_permissions__user=self.request.user)
        ).distinct().prefetch_related('accounts')


class AccountModelDetailView(UpdateView):
    context_object_name = 'account'
    pk_url_kwarg = 'account_pk'
    template_name = 'django_ledger/account_detail.html'
    form_class = AccountModelForm

    def get_success_url(self):
        return reverse('django_ledger:coa-detail',
                       kwargs={
                           'coa_slug': self.object.coa.slug
                       })

    def get_queryset(self):
        return AccountModel.objects.filter(
            Q(coa__user=self.request.user) |
            Q(coa__entitymodel__admin=self.request.user) |
            Q(coa__entitymodel__managers__in=[self.request.user])
        ).select_related('coa').distinct()


class AccountCreateView(CreateView):
    template_name = 'django_ledger/account_create.html'
    form_class = AccountModelCreateForm

    def get_success_url(self):
        return reverse('django_ledger:coa-list')

    def form_valid(self, form):
        form.save()


class LedgerModelListView(ListView):
    context_object_name = 'ledgers'
    template_name = 'django_ledger/ledger_list.html'

    def get_queryset(self):
        entity_slug = self.kwargs.get('entity_slug')
        return LedgerModel.objects.filter(
            Q(entity__slug=entity_slug) &
            Q(entity__admin=self.request.user) |
            Q(entity__managers__in=[self.request.user])
        )


class LedgerModelDetailView(DetailView):
    template_name = 'django_ledger/ledger_detail.html'
    context_object_name = 'ledger'
    pk_url_kwarg = 'ledger_pk'

    def get_queryset(self):
        entity_slug = self.kwargs.get('entity_slug')
        return LedgerModel.objects.filter(
            Q(entity__slug=entity_slug) &
            Q(entity__admin=self.request.user) |
            Q(entity__managers__in=[self.request.user])
        ).prefetch_related('journal_entry', 'entity')


class LedgerModelCreateView(CreateView):
    template_name = 'django_ledger/ledger_create.html'
    form_class = LedgerModelCreateForm

    def get_initial(self):
        slug = self.kwargs.get('entity_slug')
        return {
            'entity': EntityModel.objects.get(slug=slug)
        }

    def get_success_url(self):
        return reverse('django_ledger:ledger-list',
                       kwargs={
                           'entity_slug': self.kwargs.get('entity_slug')
                       })


class LedgerModelUpdateView(UpdateView):
    template_name = 'django_ledger/ledger_update.html'
    form_class = LedgerModelUpdateForm
    pk_url_kwarg = 'ledger_pk'
    context_object_name = 'ledger'

    def get_queryset(self):
        entity_slug = self.kwargs.get('entity_slug')
        return LedgerModel.objects.filter(
            Q(entity__slug=entity_slug) &
            Q(entity__admin=self.request.user) |
            Q(entity__managers__in=[self.request.user])
        )

    def get_success_url(self):
        return reverse('django_ledger:ledger-list',
                       kwargs={
                           'entity_slug': self.kwargs.get('entity_slug')
                       })


class JournalEntryDetailView(DetailView):
    pk_url_kwarg = 'je_pk'
    context_object_name = 'journal_entry'
    template_name = 'django_ledger/je_detail.html'

    def get_queryset(self):
        entity_slug = self.kwargs.get('entity_slug')
        return JournalEntryModel.objects.filter(
            Q(ledger__entity__slug=entity_slug) &
            Q(ledger__entity__admin=self.request.user) |
            Q(ledger__entity__managers__in=[self.request.user])
        ).prefetch_related('txs', 'txs__account')


class JournalEntryUpdateView(UpdateView):
    pk_url_kwarg = 'je_pk'
    context_object_name = 'journal_entry'
    template_name = 'django_ledger/je_update.html'
    form_class = JournalEntryModelForm

    def get_queryset(self):
        entity_slug = self.kwargs.get('entity_slug')
        return JournalEntryModel.objects.filter(
            Q(ledger__entity__slug=entity_slug) &
            Q(ledger__entity__admin=self.request.user) |
            Q(ledger__entity__managers__in=[self.request.user])
        ).prefetch_related('txs', 'txs__account')


class JournalEntryCreateView(CreateView):
    form_class = JournalEntryModelForm
    template_name = 'django_ledger/je_create.html'

    def get_initial(self):
        ledger_pk = self.kwargs.get('ledger_pk')
        return {
            'ledger': LedgerModel.objects.get(pk=ledger_pk)
        }

    def get_success_url(self):
        return reverse('django_ledger:ledger-detail',
                       kwargs={
                           'entity_slug': self.kwargs.get('entity_slug'),
                           'ledger_pk': self.kwargs.get('ledger_pk')
                       })


class TXSIOView(TemplateView):
    template_name = 'django_ledger/txs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        txs_action_url = reverse('django_ledger:txs', kwargs={
            'entity_slug': kwargs['entity_slug'],
            'ledger_pk': kwargs['ledger_pk'],
            'je_pk': kwargs['je_pk'],
        })
        context['txs_action_url'] = txs_action_url
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        je_pk = kwargs.get('je_pk')
        txs_qs = TransactionModel.objects.filter(
            journal_entry_id=je_pk
        ).select_for_update().prefetch_related('journal_entry')
        txs_formset = TransactionModelFormSet(queryset=txs_qs)
        context['txs_formset'] = txs_formset
        context['txs_qs'] = txs_qs
        return self.render_to_response(context)

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        txs_formset = TransactionModelFormSet(self.request.POST)
        if txs_formset.is_valid():
            txs_formset.save()
        context['txs_formset'] = txs_formset
        return self.render_to_response(context)
