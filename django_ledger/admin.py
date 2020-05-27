from django.contrib import admin

from django_ledger.models import (LedgerModel, EntityModel, ChartOfAccountModel, AccountModel,
                                  JournalEntryModel, TransactionModel, EntityManagementModel, InvoiceModel,
                                  BillModel)


class TransactionModelInLine(admin.TabularInline):
    model = TransactionModel


class JournalEntryModelAdmin(admin.ModelAdmin):
    readonly_fields = [
        'ledger'
    ]
    inlines = [
        TransactionModelInLine
    ]

    class Meta:
        model = JournalEntryModel


class EntityManagementInLine(admin.TabularInline):
    model = EntityManagementModel


class EntityModelAdmin(admin.ModelAdmin):
    inlines = [
        EntityManagementInLine
    ]

    class Meta:
        model = EntityModel


class AccountModelAdmin(admin.ModelAdmin):
    actions = [
        'activate',
        'inactivate',
        'lock',
        'unlock'
    ]
    actions_on_top = True
    actions_on_bottom = True
    sortable_by = [
        'code'
    ]
    list_display = [
        '__str__',
        'active',
        'locked'
    ]
    list_filter = [
        'role',
        'balance_type',
    ]

    class Meta:
        model = AccountModel

    def activate(self, request, queryset):
        queryset.update(active=True)

    def inactivate(self, request, queryset):
        queryset.update(active=False)

    def lock(self, request, queryset):
        queryset.update(locked=True)

    def unlock(self, request, queryset):
        queryset.update(locked=False)

    # def role_bs(self, acc):
    #     return acc.role_bs.upper()

    # role_bs.short_description = 'Balance Sheet Role'


class AccountsModelInLine(admin.TabularInline):
    model = AccountModel
    readonly_fields = [
        'role_bs',
        'role',
        'balance_type',
    ]


class ChartOfAccountsModelAdmin(admin.ModelAdmin):
    inlines = [
        AccountsModelInLine
    ]

    class Meta:
        model = ChartOfAccountModel


class LedgerModelAdmin(admin.ModelAdmin):
    class Meta:
        model = LedgerModel


class InvoiceModelAdmin(admin.ModelAdmin):
    readonly_fields = [
        'invoice_number',
        'due_date',
        'ledger'
    ]

    class Meta:
        model = InvoiceModel


class BillModelAdmin(admin.ModelAdmin):
    readonly_fields = [
        'bill_number',
        'due_date',
        'ledger'
    ]

    class Meta:
        model = BillModel


admin.site.register(EntityModel, EntityModelAdmin)
admin.site.register(JournalEntryModel, JournalEntryModelAdmin)
admin.site.register(LedgerModel, LedgerModelAdmin)
admin.site.register(ChartOfAccountModel, ChartOfAccountsModelAdmin)
admin.site.register(AccountModel, AccountModelAdmin)
admin.site.register(InvoiceModel, InvoiceModelAdmin)
admin.site.register(BillModel, BillModelAdmin)
