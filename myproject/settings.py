import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# ENV HELPERS
# ----------------------------
def env_bool(var_name, default=False):
    return os.environ.get(var_name, str(default)).lower() in ("1", "true", "yes")

def env_list(var_name, default=None):
    value = os.environ.get(var_name)
    if not value:
        return default or []
    return [v.strip() for v in value.split(",") if v.strip()]

# ----------------------------
# SECURITY SETTINGS
# ----------------------------

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-your-secret-key-here-for-development")

# ✅ DEVELOPMENT MODE - Set to True for development
DEBUG = False  # ✅ Set to True for development

# ✅ ALLOWED_HOSTS - Fixed for development
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '::1',  # IPv6 localhost
    'yourdomain.com',
    'www.yourdomain.com'
]

# If you want to allow all hosts during development (not recommended for production):
ALLOWED_HOSTS = ['new-project-owqg.onrender.com', 'localhost', '127.0.0.1']

# ----------------------------
# INSTALLED APPS
# ----------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",

    "myapp",
]

# ----------------------------
# MIDDLEWARE (IMPORTANT ORDER)
# ----------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ✅ UNCOMMENTED - Should be at top
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# ----------------------------
# CORS SETTINGS (Development)
# ----------------------------

CORS_ALLOW_ALL_ORIGINS = True  # ✅ Allow all for development (or use CORS_ALLOWED_ORIGINS)
CORS_ALLOW_CREDENTIALS = True

# For production, use specific origins:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
#     "http://localhost:3000",  # React dev server
#     "https://yourdomain.com",
# ]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ----------------------------
# URL / WSGI
# ----------------------------

ROOT_URLCONF = "myproject.urls"
WSGI_APPLICATION = "myproject.wsgi.application"

# ----------------------------
# SECURITY HEADERS (Development - All Disabled)
# ----------------------------

SECURE_HSTS_SECONDS = 0  # ✅ Disabled for development
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_SSL_REDIRECT = False  # ✅ Disabled for development
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SESSION_COOKIE_SECURE = False  # ✅ Disabled for development
CSRF_COOKIE_SECURE = False  # ✅ Disabled for development
X_FRAME_OPTIONS = "DENY"

# ✅ CSRF Settings for development
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
]

# ✅ Session Settings for development
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ----------------------------
# TEMPLATES
# ----------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # ✅ Add global templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ----------------------------
# DATABASE
# ----------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ----------------------------
# AUTH
# ----------------------------

AUTH_USER_MODEL = "myapp.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------
# INTERNATIONALIZATION
# ----------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------------
# STATIC / MEDIA
# ----------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------
# DRF (Development)
# ----------------------------

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # ✅ Allow any for development
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",  # ✅ Higher limit for development
        "user": "1000/day",
    },
}

# ----------------------------
# LOGGING (Development - Detailed)
# ----------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'myapp': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
