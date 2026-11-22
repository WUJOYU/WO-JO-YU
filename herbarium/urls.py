from django.urls import path
from . import views
urlpatterns=[path('',views.home,name='home'),path('records/',views.records,name='records'),path('records/<int:pk>/',views.record_detail,name='record_detail'),path('taxonomy/',views.taxonomy,name='taxonomy'),path('types/',views.type_collection,name='type_collection'),path('specimens/',views.specimens,name='specimens'),path('specimens/<int:pk>/',views.specimen_detail,name='specimen_detail'),path('exports/darwin-core.csv',views.darwin_core_export,name='darwin_core_export')]
