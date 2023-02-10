"""
Django settings for ampa_manager_project project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from os.path import join
from pathlib import Path
from django.utils.translation import gettext_lazy as _

from ampa_manager_project.secret_key_manager import SecretKeyManager

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# KEY CONFIGURATION ----------------------------------------------------------------------------------------------------
# Try to load the SECRET_KEY from our secret_file. If that fails, then generate
# a random SECRET_KEY and save it into our secret_file for future loading. If
# everything fails, then just raise an exception.

# Absolute filesystem path to the secret file which holds this project's SECRET_KEY.
secret_file = join(os.path.dirname(os.path.abspath(__file__)), './credentials/sk')
SECRET_KEY = SecretKeyManager().load_or_create_key(secret_file)
# END KEY CONFIGURATION ------------------------------------------------------------------------------------------------

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
    'ampa_manager',
    'localflavor',
    'phonenumber_field',
    'admin_reorder',
    'django_extensions',
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

ROOT_URLCONF = 'ampa_manager_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ampa_manager_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'db.sqlite3',
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

LANGUAGE_CODE = 'es-es'

LANGUAGES = [
    ('es', _('Spanish')),
    # ("en", _("English")),
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
    {'app': 'ampa_manager', 'label': _('Academic course'),
     'models': ('ampa_manager.AcademicCourse', 'ampa_manager.ActiveCourse')},
    {'app': 'ampa_manager', 'label': _('Family'),
     'models': (
         'ampa_manager.Family', 'ampa_manager.Parent', 'ampa_manager.Child',
         'ampa_manager.Membership', 'ampa_manager.BankAccount', 'ampa_manager.Holder',
         'ampa_manager.BankBicCode')},
    {'app': 'ampa_manager', 'label': _('After-school'),
     'models': (
         'ampa_manager.AfterSchool', 'ampa_manager.AfterSchoolEdition',
         'ampa_manager.AfterSchoolRegistration')},
    {'app': 'ampa_manager', 'label': _('Custody'),
     'models': (
         'ampa_manager.CustodyEdition', 'ampa_manager.CustodyRegistration')},
    {'app': 'ampa_manager', 'label': _('Charge'),
     'models': (
         'ampa_manager.Fee',
         'ampa_manager.MembershipReceipt', 'ampa_manager.MembershipRemittance',
         'ampa_manager.AfterSchoolReceipt', 'ampa_manager.AfterSchoolRemittance',
         'ampa_manager.CustodyReceipt', 'ampa_manager.CustodyRemittance',)},
    # Keep original label and models
    'auth',
)


PHONENUMBER_DB_FORMAT = 'E164'
PHONENUMBER_DEFAULT_REGION = 'ES'
PHONENUMBER_DEFAULT_FORMAT = 'NATIONAL'
