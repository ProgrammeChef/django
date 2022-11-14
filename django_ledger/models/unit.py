"""
Django Ledger created by Miguel Sanda <msanda@arrobalytics.com>.
Copyright© EDMA Group Inc licensed under the GPLv3 Agreement.

Contributions to this module:
Miguel Sanda <msanda@arrobalytics.com>
"""

from random import choices
from string import ascii_lowercase, digits, ascii_uppercase
from uuid import uuid4

from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node, MP_NodeManager

from django_ledger.io.io_mixin import IOMixIn
from django_ledger.models.mixins import CreateUpdateMixIn, SlugNameMixIn

ENTITY_UNIT_RANDOM_SLUG_SUFFIX = ascii_lowercase + digits


def create_entity_unit_slug(name, k=5):
    slug = slugify(name)
    suffix = ''.join(choices(ENTITY_UNIT_RANDOM_SLUG_SUFFIX, k=k))
    unit_slug = f'{slug}-{suffix}'
    return unit_slug


class EntityUnitModelQuerySet(models.QuerySet):
    pass


class EntityUnitModelManager(MP_NodeManager):

    def for_entity(self, entity_slug: str, user_model):
        qs = self.get_queryset()
        return qs.filter(
            Q(entity__slug__exact=entity_slug) &
            (
                    Q(entity__admin=user_model) |
                    Q(entity__managers__in=[user_model])
            )

        )


class EntityUnitModelAbstract(MP_Node, IOMixIn, SlugNameMixIn, CreateUpdateMixIn):
    uuid = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    slug = models.SlugField(max_length=50)
    entity = models.ForeignKey('django_ledger.EntityModel',
                               editable=False,
                               on_delete=models.CASCADE,
                               verbose_name=_('Unit Entity'))
    document_prefix = models.CharField(max_length=3)
    active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    hidden = models.BooleanField(default=False, verbose_name=_('Is Hidden'))

    objects = EntityUnitModelManager.from_queryset(queryset_class=EntityUnitModelQuerySet)()
    node_order_by = ['uuid']

    class Meta:
        abstract = True
        ordering = ['-created']
        verbose_name = _('Entity Unit Model')
        unique_together = [
            ('entity', 'slug'),
            ('entity', 'document_prefix'),
        ]
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['hidden']),
            models.Index(fields=['entity']),
        ]

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return self.name

    def clean(self):
        if not self.slug:
            self.slug = create_entity_unit_slug(self.name)

        if not self.document_prefix:
            self.document_prefix = ''.join(choices(ascii_uppercase, k=3))

    def get_dashboard_url(self):
        return reverse('django_ledger:unit-dashboard',
                       kwargs={
                           'entity_slug': self.slug
                       })

    def save(self, **kwargs):
        self.clean()
        super(EntityUnitModelAbstract, self).save(self, **kwargs)


class EntityUnitModel(EntityUnitModelAbstract):
    """
    Base Model Class for EntityUnitModel
    """
