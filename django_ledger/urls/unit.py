from django.urls import path

from django_ledger import views

urlpatterns = [
    path('<slug:entity_slug>/unit/list/',
         views.EntityUnitModelListView.as_view(),
         name='unit-list'),
    path('<slug:entity_slug>/detail/<slug:unit_slug>/',
         views.EntityUnitModelDetailView.as_view(),
         name='unit-detail'),
    path('<slug:entity_slug>/unit/create/',
         views.EntityUnitModelCreateView.as_view(),
         name='unit-create'),
    path('<slug:entity_slug>/unit/update/<slug:unit_slug>/',
         views.EntityUnitUpdateView.as_view(),
         name='unit-update'),


    # DASHBOARD Views ...
    path('<slug:entity_slug>/dashboard/<slug:unit_slug>/',
         views.EntityModelDetailView.as_view(),
         name='unit-dashboard'),
    path('<slug:entity_slug>/dashboard/<slug:unit_slug>/year/<int:year>/',
         views.FiscalYearEntityModelDashboardView.as_view(),
         name='unit-dashboard-year'),
    path('<slug:entity_slug>/dashboard/<slug:unit_slug>/quarter/<int:year>/<int:quarter>/',
         views.QuarterlyEntityDashboardView.as_view(),
         name='unit-dashboard-quarter'),
    path('<slug:entity_slug>/dashboard/<slug:unit_slug>/month/<int:year>/<int:month>/',
         views.MonthlyEntityDashboardView.as_view(),
         name='unit-dashboard-month'),
    path('<slug:entity_slug>/dashboard/<slug:unit_slug>/date/<int:year>/<int:month>/<int:day>/',
         views.DateEntityDashboardView.as_view(),
         name='unit-dashboard-date'),

]
