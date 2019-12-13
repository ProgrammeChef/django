from random import randint

from django.db.models.signals import pre_save
from django.utils.text import slugify

from django_ledger.models.coa import ChartOfAccountModel
from django_ledger.models_abstracts.entity import EntityModelAbstract, EntityManagementModelAbstract


class EntityModel(EntityModelAbstract):
    """
    Entity Model Base Class From Abstract
    """


def entity_presave(sender, instance, **kwargs):
    if not instance.slug:
        slug = slugify(instance.name)
        ri = randint(100000, 999999)
        entity_slug = f'{slug}-{ri}'
        instance.slug = entity_slug

    if not getattr(instance, 'coa', None):
        new_coa = ChartOfAccountModel.objects.create(
            slug=instance.slug + '-coa',
            name=instance.name + ' CoA'
        )
        instance.coa = new_coa


pre_save.connect(entity_presave, EntityModel)


class EntityManagementModel(EntityManagementModelAbstract):
    """
    EntityManagement Model Base Class From Abstract
    """
