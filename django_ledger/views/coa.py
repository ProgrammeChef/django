from django.urls import reverse
from django.utils.translation import gettext_lazy as _l
from django.views.generic import UpdateView

from django_ledger.forms import ChartOfAccountsModelUpdateForm
from django_ledger.models import ChartOfAccountModel


class ChartOfAccountsUpdateView(UpdateView):
    context_object_name = 'coa'
    slug_url_kwarg = 'coa_slug'
    template_name = 'django_ledger/coa_update.html'
    form_class = ChartOfAccountsModelUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _l('CoA: ') + self.object.name
        context['header_title'] = _l('CoA: ') + self.object.name
        return context

    def get_success_url(self):
        entity_slug = self.kwargs.get('entity_slug')
        return reverse('django_ledger:entity-detail',
                       kwargs={
                           'entity_slug': entity_slug
                       })

    def get_queryset(self):
        return ChartOfAccountModel.objects.for_user(
            user=self.request.user
        ).distinct()