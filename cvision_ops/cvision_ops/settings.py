"""
Django settings for cvision_ops project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--ymmm380tdk@rm=en@8e8!qeh2%80*cx!3o98-#-#+h6i$3t*3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS', '0.0.0.0')]


# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'users',
    'metadata',
    'tenants',
    'images',
    'projects',
    'database',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cvision_ops.urls'
AUTH_USER_MODEL = "users.CustomUser"

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

WSGI_APPLICATION = 'cvision_ops.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', "django.db.backends.sqlite3"),
        'NAME': os.environ.get('DATABASE_NAME') if not 'sqlite3' in os.environ.get('DATABASE_ENGINE') else BASE_DIR / 'db.sqlite3',
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT')

    }
}

# # Azure Storage Configuration
if os.getenv('DJANGO_STORAGE', 'local') == "azure":
    AZURE_ACCOUNT_NAME = "wacoreblob"
    AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
    AZURE_CONTAINER = "cvisionops/media"
    AZURE_URL_EXPIRATION_SECS = 3600 

    AZURE_CONNECTION_STRING = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={AZURE_ACCOUNT_NAME};"
        f"AccountKey={AZURE_ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net;"
        f"BlobEndpoint=https://wacoreblob.blob.core.windows.net/cvisionops"
    )

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "connection_string": AZURE_CONNECTION_STRING,
                "azure_container": AZURE_CONTAINER,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "connection_string": AZURE_CONNECTION_STRING,
                "azure_container": "cvisionops/static",
            },
        },
    }



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = 'media/'
MEDIA_ROOT = '/media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

UNFOLD = {
    "SITE_HEADER": _("RTCVision"),
    "SITE_TITLE": _("Reat-Time Computer Vision"),
    "SITE_SYMBOL": "RTCVision",
    "SITE_ICON": {
        "light": lambda request: static("icon-light.svg"),  # light mode
        "dark": lambda request: static("icon-dark.svg"),  # dark mode
    },
    "SITE_LOGO": lambda request: static("images/logo.jpg"),  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("logo-light.svg"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "46x32",
            "type": "image/svg+xml",
            "href": lambda request: static("favicon.svg"),
        },
    ],
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    # "THEME": "dark", # Force theme: "dark" or "light". Will disable theme switcher
    "LOGIN": {
        "image": lambda request: static("images/login.jpeg"),
        "redirect_after": lambda request: reverse_lazy("admin:tenants_tenant_changelist"),
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "de": "🇩🇪",
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Navigation"),
                "items": [
                    {
                        "title": _("All Apps"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ]
            },
            {
                "title": _("Tenant"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Tenant"),
                        "icon": 'tenancy',
                        "link": reverse_lazy(
                            "admin:tenants_tenant_changelist"
                        ),
                    },
                    {
                        "title": _("Plant"),
                        "icon": 'local_fire_department',
                        "link": reverse_lazy(
                            "admin:tenants_plant_changelist"
                        ),
                    },
                    {
                        "title": _("Domain"),
                        "icon": 'domain',
                        "link": reverse_lazy(
                            "admin:tenants_domain_changelist"
                        ),
                    },
                    {
                        "title": _("Edge Boxes"),
                        "icon": 'devices',
                        "link": reverse_lazy(
                            "admin:tenants_edgebox_changelist"
                        ),
                    },
                    {
                        "title": _("SensorBoxes"),
                        "icon": 'sensors',
                        "link": reverse_lazy(
                            "admin:tenants_sensorbox_changelist"
                        ),
                    },
                ]
            },
            {
                "title": _("Users & Groups"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy(
                            "admin:users_customuser_changelist"
                            ),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy(
                            "admin:auth_group_changelist"
                            ),
                    }
                ],
            },
            {
                "title": _("MetaData"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Languages"),
                        "icon": "language",
                        "link": reverse_lazy(
                            "admin:metadata_language_changelist"
                        ),
                    },
                ],
            },
            {
                "title": _("Images"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Image Mode"),
                        "icon": 'imagesmode',
                        "link": reverse_lazy(
                            "admin:images_imagemode_changelist"
                        ),
                    },
                    {
                        "title": _("Images"),
                        "icon": 'image',
                        "link": reverse_lazy(
                            "admin:images_image_changelist"
                        ),
                    },
                ]
            },
            {
                "title": _("Projects"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Project Types"),
                        "icon": 'imagesmode',
                        "link": reverse_lazy(
                            "admin:projects_projecttype_changelist"
                        ),
                    },
                    {
                        "title": _("Images"),
                        "icon": 'image',
                        "link": reverse_lazy(
                            "admin:images_image_changelist"
                        ),
                    },
                ]
            },
 
        ],
    },
}