from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import localdate
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DetailView, RedirectView

from django_ledger.forms.unit import EntityUnitModelCreateForm, EntityUnitModelUpdateForm
from django_ledger.models import EntityUnitModel, EntityModel
from django_ledger.views.entity import (
    FiscalYearEntityModelBalanceSheetView, FiscalYearEntityModelIncomeStatementView,
    FiscalYearEntityModelCashFlowStatementView)
from django_ledger.views.mixins import (DjangoLedgerSecurityMixIn, QuarterlyReportMixIn, MonthlyReportMixIn,
                                        DateReportMixIn)


class EntityUnitModelListView(DjangoLedgerSecurityMixIn, ListView):
    template_name = 'django_ledger/unit/unit_list.html'
    PAGE_TITLE = _('Entity Unit List')
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        # 'header_subtitle_icon': 'dashicons:businesswoman'
    }
    context_object_name = 'unit_list'

    def get_queryset(self):
        return EntityUnitModel.objects.for_entity(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user
        ).select_related('entity')


class EntityUnitModelDetailView(DjangoLedgerSecurityMixIn, DetailView):
    template_name = 'django_ledger/unit/unit_detail.html'
    PAGE_TITLE = _('Entity Unit Detail')
    slug_url_kwarg = 'unit_slug'
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        # 'header_subtitle_icon': 'dashicons:businesswoman'
    }
    context_object_name = 'unit'

    def get_queryset(self):
        return EntityUnitModel.objects.for_entity(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user
        ).select_related('entity')


class EntityUnitModelCreateView(DjangoLedgerSecurityMixIn, CreateView):
    template_name = 'django_ledger/unit/unit_create.html'
    PAGE_TITLE = _('Entity Unit Create')
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        # 'header_subtitle_icon': 'dashicons:businesswoman'
    }

    def get_form(self, form_class=None):
        return EntityUnitModelCreateForm(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user,
            **self.get_form_kwargs()
        )

    def get_success_url(self):
        return reverse('django_ledger:unit-list',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug']
                       })

    def form_valid(self, form):
        entity_unit_model: EntityUnitModel = form.save(commit=False)
        entity_model = get_object_or_404(EntityModel, slug=self.kwargs['entity_slug'])
        EntityUnitModel.add_root(**form.cleaned_data, entity=entity_model)
        return HttpResponseRedirect(self.get_success_url())


class EntityUnitUpdateView(DjangoLedgerSecurityMixIn, UpdateView):
    template_name = 'django_ledger/unit/unit_update.html'
    PAGE_TITLE = _('Entity Unit Update')
    slug_url_kwarg = 'unit_slug'
    context_object_name = 'unit'
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        # 'header_subtitle_icon': 'dashicons:businesswoman'
    }

    def get_queryset(self):
        return EntityUnitModel.objects.for_entity(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user
        ).select_related('entity')

    def get_form(self, form_class=None):
        return EntityUnitModelUpdateForm(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user,
            **self.get_form_kwargs()
        )

    def get_success_url(self):
        return reverse('django_ledger:unit-list',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug']
                       })

    def form_valid(self, form):
        instance: EntityUnitModel = form.save(commit=False)
        instance.clean()
        form.save()
        return super().form_valid(form=form)


# Financial Statements...


# BALANCE SHEET.....
class EntityUnitModelBalanceSheetView(DjangoLedgerSecurityMixIn, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        year = localdate().year
        return reverse('django_ledger:unit-bs-year',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug'],
                           'unit_slug': self.kwargs['unit_slug'],
                           'year': year
                       })


class FiscalYearEntityUnitModelBalanceSheetView(FiscalYearEntityModelBalanceSheetView):
    """
    Entity Unit Fiscal Year Balance Sheet View Class
    """

    context_object_name = 'unit_model'
    slug_url_kwarg = 'unit_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_model'] = self.object.entity
        return context

    def get_queryset(self):
        return EntityUnitModel.objects.for_entity(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user
        ).select_related('entity')

    def get_fy_start_month(self) -> int:
        entity_unit: EntityUnitModel = self.object
        return entity_unit.entity.fy_start_month


class QuarterlyEntityUnitModelBalanceSheetView(QuarterlyReportMixIn, FiscalYearEntityUnitModelBalanceSheetView):
    """
    Entity Unit Fiscal Quarter Balance Sheet View Class.
    """


class MonthlyEntityUnitModelBalanceSheetView(MonthlyReportMixIn, FiscalYearEntityUnitModelBalanceSheetView):
    """
    Entity Unit Fiscal Month Balance Sheet View Class.
    """


class DateEntityUnitModelBalanceSheetView(DateReportMixIn, MonthlyEntityUnitModelBalanceSheetView):
    """
    Entity Unit Date Balance Sheet View Class.
    """


# INCOME STATEMENT....
class EntityUnitModelIncomeStatementView(DjangoLedgerSecurityMixIn, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        year = localdate().year
        return reverse('django_ledger:unit-ic-year',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug'],
                           'unit_slug': self.kwargs['unit_slug'],
                           'year': year
                       })


class FiscalYearEntityUnitModelIncomeStatementView(FiscalYearEntityModelIncomeStatementView):
    """
    Entity Unit Fiscal Quarter Income Statement View Class
    """


class QuarterlyEntityUnitModelIncomeStatementView(QuarterlyReportMixIn, FiscalYearEntityModelIncomeStatementView):
    """
    Entity Unit Fiscal Quarter Income Statement View Class
    """


class MonthlyEntityUnitModelIncomeStatementView(MonthlyReportMixIn, FiscalYearEntityModelIncomeStatementView):
    """
    Entity Unit Fiscal Month Income Statement View Class
    """


class DateEntityUnitModelIncomeStatementView(DateReportMixIn, FiscalYearEntityModelIncomeStatementView):
    """
    Entity Unit Date Income Statement View Class
    """


# CASHFLOW STATEMENT
class EntityUnitModelCashFlowStatementView(DjangoLedgerSecurityMixIn, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        year = localdate().year
        return reverse('django_ledger:unit-cf-year',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug'],
                           'unit_slug': self.kwargs['unit_slug'],
                           'year': year
                       })


class FiscalYearEntityUnitModelCashFlowStatementView(FiscalYearEntityModelCashFlowStatementView):
    """
    Entity Unit Fiscal Quarter Cash Flow Statement View Class
    """


class QuarterlyEntityUnitModelCashFlowStatementView(QuarterlyReportMixIn,
                                                    FiscalYearEntityUnitModelCashFlowStatementView):
    """
    Entity Unit Fiscal Quarter Cash Flow Statement View Class
    """


class MonthlyEntityUnitModelCashFlowStatementView(MonthlyReportMixIn, FiscalYearEntityUnitModelCashFlowStatementView):
    """
    Entity Unit Fiscal Month Cash Flow Statement View Class
    """


class DateEntityUnitModelCashFlowStatementView(DateReportMixIn, FiscalYearEntityUnitModelCashFlowStatementView):
    """
    Entity Unit Date Cash Flow Statement View Class
    """
