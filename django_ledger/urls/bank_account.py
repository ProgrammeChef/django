from django.urls import path

from django_ledger import views

urlpatterns = [
    path('<slug:entity_slug>/list/',
         views.BankAccountModelListView.as_view(),
         name='bank-account-list'),
    path('<slug:entity_slug>/create/',
         views.BankAccountModelCreateView.as_view(),
         name='bank-account-create'),
    path('<slug:entity_slug>/update/<uuid:bank_account_pk>/',
         views.BankAccountModelUpdateView.as_view(),
         name='bank-account-update'),
]
