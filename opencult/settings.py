"""
Django settings for opencult project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('OPENCULT_SECRET_KEY', 'thiswillbeoursecret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv('NODEBUG') is None else False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'opencult.com',
]


# Application definition

INSTALLED_APPS = [
    'main.apps.MainConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'opencult.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'opencult.wsgi.application'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTH_TOKEN_DURATION = 30 * 60  # = 1800 = 30 min in seconds


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'opencult',
        'USER': 'opencult',
        'PASSWORD': 'opencult',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Update database configuration with $DATABASE_URL.
# https://devcenter.heroku.com/articles/django-app-configuration#database-configuration
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')


# Email
# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
EMAIL_HOST_USER = os.getenv('OPENCULT_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('OPENCULT_EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = 'hi@opencult.com'
EMAIL_ALERT = 'theodorekeloglou@gmail.com'


# Authentication backends
# https://docs.djangoproject.com/en/1.11/topics/auth/customizing/

AUTHENTICATION_BACKENDS = (
    'main.auth_backends.EmailTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# Security middleware
# https://docs.djangoproject.com/en/1.11/ref/middleware/#module-django.middleware.security

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True


# Celery settings
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://@localhost:6379/1')
