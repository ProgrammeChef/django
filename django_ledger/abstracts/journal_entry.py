from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.http import Http404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from mptt.models import MPTTModel

# todo: this is creating a circular reference need to resolve.
# from django_ledger.abstracts.mixins import CreateUpdateMixIn

ACTIVITIES = [
    ('op', _('Operating')),
    ('fin', _('Financing')),
    ('inv', _('Investing')),
    ('other', _('Other')),
]

ACTIVITY_ALLOWS = [a[0] for a in ACTIVITIES]
ACTIVITY_IGNORE = ['all']


def validate_activity(activity: str, raise_404: bool = False):
    if activity:

        if activity in ACTIVITY_IGNORE:
            activity = None

        # todo: temporary fix. User should be able to pass a list.
        if isinstance(activity, list) and len(activity) == 1:
            activity = activity[0]
        elif isinstance(activity, list) and len(activity) > 1:
            exception = ValidationError(f'Multiple activities passed {activity}')
            if raise_404:
                raise Http404(exception)
            raise exception

        valid = activity in ACTIVITY_ALLOWS
        if activity and not valid:
            exception = ValidationError(f'{activity} is invalid. Choices are {ACTIVITY_ALLOWS}.')
            if raise_404:
                raise Http404(exception)
            raise exception

    return activity


class JournalEntryModelManager(models.Manager):

    def for_ledger(self, ledger_slug: str, entity_slug: str, user_model):
        # if isinstance(ledger, str):
        #     qs = self.get_queryset().filter(ledger__slug__iexact=ledger)
        # else:
        #     qs = self.get_queryset().filter(ledger=ledger)

        qs = self.get_queryset().filter(
            Q(ledger__slug__iexact=ledger_slug) &
            Q(ledger__entity__slug__iexact=entity_slug) &
            (
                    Q(ledger__entity__admin=user_model) |
                    Q(ledger__entity__managers__in=[user_model])
            )

        )
        return qs

    # def on_ledger_posted(self, ledger):
    #     return self.on_ledger(ledger=ledger).filter(
    #         posted=True,
    #         ledger__posted=True
    #     )


class JournalEntryModelAbstract(MPTTModel):
    date = models.DateField(verbose_name=_l('Date'))
    description = models.CharField(max_length=70, blank=True, null=True, verbose_name=_l('Description'))
    activity = models.CharField(choices=ACTIVITIES, max_length=5, verbose_name=_l('Activity'))
    origin = models.CharField(max_length=30, blank=True, null=True, verbose_name=_l('Origin'))
    posted = models.BooleanField(default=False, verbose_name=_l('Posted'))
    locked = models.BooleanField(default=False, verbose_name=_l('Locked'))
    parent = models.ForeignKey('self',
                               blank=True,
                               null=True,
                               verbose_name=_l('Parent'),
                               related_name='children',
                               on_delete=models.CASCADE)
    ledger = models.ForeignKey('django_ledger.LedgerModel',
                               verbose_name=_l('Ledger'),
                               related_name='journal_entries',
                               on_delete=models.CASCADE)

    # todo: must come from create/update mixin. Resolve circular reference.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    on_coa = JournalEntryModelManager()

    class Meta:
        abstract = True
        ordering = ['-created']
        verbose_name = _l('Journal Entry')
        verbose_name_plural = _l('Journal Entries')
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['activity']),
            models.Index(fields=['ledger']),
            models.Index(fields=['date', 'ledger', 'activity', 'posted']),
        ]

    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return 'JE ID: {x1} - Desc: {x2}'.format(x1=self.pk, x2=self.description)

    def get_absolute_url(self):
        return reverse('django_ledger:je-detail',
                       kwargs={
                           'je_pk': self.id,
                           'ledger_pk': self.ledger_id,
                           'entity_slug': self.ledger.entity.slug
                       })

    def get_balances(self):
        txs = self.txs.only('tx_type', 'amount')
        credits = txs.filter(tx_type__iexact='credit').aggregate(Sum('amount'))
        debits = txs.filter(tx_type__iexact='debit').aggregate(Sum('amount'))
        balances = {
            'credits': credits['amount__sum'],
            'debits': debits['amount__sum']
        }
        return balances

    def je_is_valid(self):
        balances = self.get_balances()
        return balances['credits'] == balances['debits']

    def clean(self):
        check1 = 'Debits and credits do not match.'
        if not self.je_is_valid():
            raise ValidationError(check1)

    def save(self, *args, **kwargs):
        try:
            self.clean_fields()
            self.clean()
        except ValidationError:
            self.txs.all().delete()
            raise ValidationError('Something went wrong cleaning journal entry ID: {x1}'.format(x1=self.id))
        super().save(*args, **kwargs)
