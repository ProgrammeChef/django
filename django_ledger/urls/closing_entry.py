from django.urls import path

from django_ledger import views

urlpatterns = [
    path('<slug:entity_slug>/latest/',
         views.ClosingEntryModelListView.as_view(),
         name='closing-entry-list'),
    path('<slug:entity_slug>/list/year/<int:year>/',
         views.ClosingEntryModelYearListView.as_view(),
         name='closing-entry-list-year'),
    path('<slug:entity_slug>/list/month/<int:year>/<int:month>/',
         views.ClosingEntryModelMonthListView.as_view(),
         name='closing-entry-list-month'),
    path('<slug:entity_slug>/create/',
         views.ClosingEntryModelCreateView.as_view(),
         name='closing-entry-create'),
]
