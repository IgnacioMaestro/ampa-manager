"""
Django settings for ampa_members_manager_project project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gdxs^$mn=vxt41(b8+tf)g3s(-09m1j%kfj6i=7=pi$dagj1--'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ampa_members_manager',
    'localflavor',
    'phonenumber_field',
    'admin_reorder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'ampa_members_manager_project.urls'

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

WSGI_APPLICATION = 'ampa_members_manager_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ("en", _("English")),
    ('es', _('Spanish')),
    ('eu', _('Basque')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

LOCALE_PATHS = [
    '/locale'
]

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

MEDIA_ROOT = 'media/'
MEDIA_URL = ''

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_REORDER = (
    {'app': 'ampa_members_manager', 'label': _('Academic course'),
     'models': ('ampa_members_manager.AcademicCourse', 'ampa_members_manager.ActiveCourse')},
    {'app': 'ampa_members_manager', 'label': _('Family'),
     'models': (
         'ampa_members_manager.Family', 'ampa_members_manager.Parent', 'ampa_members_manager.Child',
         'ampa_members_manager.Parent', 'ampa_members_manager.Membership', 'ampa_members_manager.BankAccount',
         'ampa_members_manager.Authorization')},
    {'app': 'ampa_members_manager', 'label': _('Activity'),
     'models': (
         'ampa_members_manager.Activity', 'ampa_members_manager.RepetitiveActivity',
         'ampa_members_manager.UniqueActivity', 'ampa_members_manager.ActivityPayablePart')},
    {'app': 'ampa_members_manager', 'label': _('ActivityRegistration'),
     'models': ('ampa_members_manager.ActivityRegistration',)},
    {'app': 'ampa_members_manager', 'label': _('Charge'),
     'models': ('ampa_members_manager.ActivityReceipt', 'ampa_members_manager.ActivityRemittance')},
    # Keep original label and models
    'auth',
)
