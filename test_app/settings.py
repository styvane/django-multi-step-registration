"""
Django settings for registration project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure--op_cmu0g)%ksu7%ja@42xscv061)w^+w_e4eb1_$4(f_g&1-a"

DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "registration",
    "test_app",
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


ROOT_URLCONF = "test_app.urls_default"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_EMAIL_SUBJECT_PREFIX = "[Django Registration Test App]"
SEND_ACTIVATION_EMAIL = True
REGISTRATION_AUTO_LOGIN = False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1

ADMINS = (
    ("admin1", "admin1@mail.server.com"),
    ("admin2", "admin2@mail.server.com"),
)


REGISTRATION_ADMINS = (
    ("admin1", "registration_admin1@mail.server.com"),
    ("admin2", "registration_admin2@mail.server.com"),
)


USE_TZ = False
