from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from django_ledger.forms.unit import EntityUnitModelCreateForm, EntityUnitModelUpdateForm
from django_ledger.models import EntityUnitModel, EntityModel
from django_ledger.views.mixins import LoginRequiredMixIn


class EntityUnitModelListView(LoginRequiredMixIn, ListView):
    template_name = 'django_ledger/unit_list.html'
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
        )


class EntityUnitModelDetailView(LoginRequiredMixIn, DetailView):
    template_name = 'django_ledger/unit_detail.html'
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
        )


class EntityUnitModelCreateView(LoginRequiredMixIn, CreateView):
    template_name = 'django_ledger/unit_create.html'
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
        instance: EntityUnitModel = form.save(commit=False)
        entity_model = get_object_or_404(EntityModel, slug=self.kwargs['entity_slug'])
        instance.entity = entity_model
        instance.full_clean()
        form.save()
        return super().form_valid(form=form)


class EntityUnitUpdateView(LoginRequiredMixIn, UpdateView):
    template_name = 'django_ledger/unit_update.html'
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
        )

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
        instance.full_clean()
        form.save()
        return super().form_valid(form=form)
