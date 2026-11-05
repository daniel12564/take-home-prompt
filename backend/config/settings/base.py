import os
from datetime import date
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SEED_DIR = BASE_DIR / 'seed'


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'insecure-change-me')

DEBUG = env_bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',
    'activity',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', 'postgres://relay:relay@localhost:5432/relay'),
        conn_max_age=60,
    ),
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = True

STATIC_URL = '/static/'

# The dashboard has no authentication in this version (see GLOSSARY: Customer Admin).
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'UNAUTHENTICATED_USER': None,
    'EXCEPTION_HANDLER': 'core.exceptions.exception_handler',
}

# The dashboard treats this fixed date as 'today' (see GLOSSARY: Reference Date); the seed ends on
# 2026-07-27, so the real date would produce an empty dashboard.
DASHBOARD_REFERENCE_DATE = date(2026, 7, 27)
# First day with seeded Activity Events; the first selectable Reporting Week is the Monday on or after it.
DASHBOARD_DATA_START_DATE = date(2026, 2, 1)

# Every constant of the normality rules (see ADR-0001 and PLAN_REFINED 3.5); nothing else may hardcode them.
# The rollup_* and one_day_* keys are consumed by the Account-wide Findings.
DASHBOARD_RULES = {
    'baseline_weeks': 8,
    'min_baseline_weeks': 4,
    'tolerance_abs_min': 3,
    'tolerance_rel': 0.30,
    'tolerance_sqrt_factor': 1.5,
    'critical_tolerance_multiple': 2,
    'rollup_min_locations': 3,
    'rollup_min_share': 0.5,
    'one_day_concentration_share': 0.6,
}
