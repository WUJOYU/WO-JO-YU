from django.http import Http404
from django.urls import path
from django.views.generic import TemplateView
from herbarium import views

def disabled(request, *args, **kwargs):
    raise Http404("Not available in preview")

urlpatterns = [
    path("", views.home, name="home"),
    path("records/", views.records, name="records"),
    path("records/<int:pk>/", views.record_detail, name="record_detail"),
    path("taxonomy/", views.taxonomy, name="taxonomy"),
    path("specimens/", views.specimens, name="specimens"),
    path(
        "about-data/",
        TemplateView.as_view(
            template_name="herbarium/about_data.html"
        ),
        name="about_data",
    ),
    path("types/", disabled, name="type_collection"),
    path("specimens/<int:pk>/", disabled, name="specimen_detail"),
    path("exports/darwin-core.csv", disabled, name="darwin_core_export"),
]
