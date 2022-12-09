"""
Django Ledger created by Miguel Sanda <msanda@arrobalytics.com>.
Copyright© EDMA Group Inc licensed under the GPLv3 Agreement.

Contributions to this module:
    * Miguel Sanda <msanda@arrobalytics.com>
    * Pranav P Tulshyan <ptulshyan77@gmail.com>

Chart Of Accounts
_________________

A Chart of Accounts (CoA) is a collection of accounts logically grouped into a distinct set within a
ChartOfAccountModel. The CoA is the backbone of making of any financial statements and it consist of accounts of many
roles, such as cash, accounts receivable, expenses, liabilities, income, etc. For instance, we can have a heading as
"Fixed Assets" in the Balance Sheet, which will consists of Tangible, Intangible Assets. Further, the tangible assets
will consists of multiple accounts like Building, Plant & Equipments, Machinery. So, aggregation of balances of
individual accounts based on the Chart of Accounts and AccountModel roles, helps in preparation of the Financial
Statements.

All EntityModel must have a default CoA to be able to create any type of transaction. Throughout the application,
when no explicit CoA is specified, the default behavior is to use the EntityModel default CoA. **Only ONE Chart of
Accounts can be used when creating Journal Entries**. No commingling between CoAs is allowed in order to preserve the
integrity of the Journal Entry.
"""

from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from django_ledger.models import lazy_loader
from django_ledger.models.mixins import CreateUpdateMixIn, SlugNameMixIn

UserModel = get_user_model()


class ChartOfAccountQuerySet(models.QuerySet):
    pass


class ChartOfAccountModelManager(models.Manager):
    """
    A custom defined ChartOfAccountModelManager that will act as an interface to handling the initial DB queries
    to the ChartOfAccountModel.
    """

    def for_user(self, user_model) -> ChartOfAccountQuerySet:
        """
        Fetches a QuerySet of ChartOfAccountModel that the UserModel as access to. May include ChartOfAccountModel from
        multiple Entities. The user has access to bills if:
            1. Is listed as Manager of Entity.
            2. Is the Admin of the Entity.

        Parameters
        __________
        user_model
            Logged in and authenticated django UserModel instance.

        Examples
        ________
            >>> request_user = self.request.user
            >>> coa_model_qs = ChartOfAccountModel.objects.for_user(user_model=request_user)

        Returns
        _______
        ChartOfAccountQuerySet
            Returns a ChartOfAccountQuerySet with applied filters.
        """
        qs = self.get_queryset()
        return qs.filter(
            (
                    Q(entity__admin=user_model) |
                    Q(entity__managers__in=[user_model])
            )
        )

    def for_entity(self, entity_slug, user_model) -> ChartOfAccountQuerySet:
        """
        Fetches a QuerySet of ChartOfAccountsModel associated with a specific EntityModel & UserModel.
        May pass an instance of EntityModel or a String representing the EntityModel slug.

        Parameters
        __________

        entity_slug: str or EntityModel
            The entity slug or EntityModel used for filtering the QuerySet.

        user_model
            Logged in and authenticated django UserModel instance.

        Examples
        ________

            >>> request_user = self.request.user
            >>> slug = self.kwargs['entity_slug'] # may come from request kwargs
            >>> coa_model_qs = ChartOfAccountModelManager.objects.for_entity(user_model=request_user, entity_slug=slug)

        Returns
        _______
        ChartOfAccountQuerySet
            Returns a ChartOfAccountQuerySet with applied filters.
        """

        qs = self.get_queryset()
        EntityModel = lazy_loader.get_entity_model()

        if isinstance(entity_slug, str):
            return qs.filter(
                Q(entity__slug__iexact=entity_slug) &
                (
                        Q(entity__admin=user_model) |
                        Q(entity__managers__in=[user_model])
                )
            )

        elif isinstance(entity_slug, EntityModel):
            return qs.filter(
                Q(entity=entity_slug) &
                (
                        Q(entity__admin=user_model) |
                        Q(entity__managers__in=[user_model])
                )
            )


class ChartOfAccountModelAbstract(SlugNameMixIn, CreateUpdateMixIn):
    """
    Base implementation of Chart of Accounts Model as an Abstract.
    
    2. :func:`CreateUpdateMixIn <django_ledger.models.mixins.SlugMixIn>`
    2. :func:`CreateUpdateMixIn <django_ledger.models.mixins.CreateUpdateMixIn>`
    
    Attributes
    __________

    uuid : UUID
        This is a unique primary key generated for the table. The default value of this field is uuid4().

    entity: EntityModel
        The EntityModel associated with this Chart of Accounts.

    locked: bool
        This determines whether any changes can be done to the Chart of Accounts.
        Before making any update to the ChartOf Account, the account needs to be unlocked.
        Default value is set to False (unlocked).

    description: str
        A user generated description for this Chart of Accounts.
    """

    uuid = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    entity = models.ForeignKey('django_ledger.EntityModel',
                               editable=False,
                               verbose_name=_('Entity'),
                               on_delete=models.CASCADE)
    locked = models.BooleanField(default=False, verbose_name=_('Locked'))
    description = models.TextField(verbose_name=_('CoA Description'), null=True, blank=True)
    objects = ChartOfAccountModelManager.from_queryset(queryset_class=ChartOfAccountQuerySet)()

    class Meta:
        abstract = True
        ordering = ['-created']
        verbose_name = _('Chart of Account')
        verbose_name_plural = _('Chart of Accounts')
        indexes = [
            models.Index(fields=['entity'])
        ]

    def __str__(self):
        return f'{self.slug}: {self.name}'


class ChartOfAccountModel(ChartOfAccountModelAbstract):
    """
    Base ChartOfAccounts Model
    """
