from django.urls import include, path
# Intentionally no /admin/, login, or media-serving route in the preview.
urlpatterns = [path('', include('herbarium.urls'))]
