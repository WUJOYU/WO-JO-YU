import os

from .settings_demo import *

# Allow Render's HTTPS domain and local Docker testing.
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
]

# Render terminates HTTPS before forwarding requests to Django.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

DEBUG = False

# Keep the approved demo routes and password protection
# inherited from settings_demo.py.
