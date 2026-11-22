import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-only-change-me-before-deployment')
DEBUG = os.getenv('DJANGO_DEBUG', '1').lower() in ('1','true','yes')
ALLOWED_HOSTS = [x.strip() for x in os.getenv('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if x.strip()]
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions',
    'django.contrib.messages','django.contrib.staticfiles','herbarium',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware','django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
if os.getenv('POSTGRES_HOST'):
    DATABASES = {'default': {'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('POSTGRES_DB','tcf_herbarium'),'USER':os.getenv('POSTGRES_USER','tcf_user'),'PASSWORD':os.getenv('POSTGRES_PASSWORD',''),'HOST':os.getenv('POSTGRES_HOST','db'),'PORT':os.getenv('POSTGRES_PORT','5432'),'CONN_MAX_AGE':60}}
else:
    DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = [
 {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
 {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE='zh-hant'
TIME_ZONE='Asia/Taipei'
USE_I18N=True
USE_TZ=True
STATIC_URL='static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
MEDIA_URL='media/'
MEDIA_ROOT=BASE_DIR/'media'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='login'
LOGIN_REDIRECT_URL='admin:index'
LOGOUT_REDIRECT_URL='home'
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS='DENY'
