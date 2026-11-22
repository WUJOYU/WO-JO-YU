import os
from .settings import *
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.trycloudflare.com']
ROOT_URLCONF = 'config.urls_demo'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'data' / 'demo.sqlite3'}}
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STORAGES = {'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# HTTPS is enforced by the protected Cloudflare tunnel; local HTTP stays available for checks.
SECURE_SSL_REDIRECT = False

MIDDLEWARE.insert(0, 'config.demo_auth.DemoBasicAuthMiddleware')
