import os

from room_reservation.settings import prod as config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = config.BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Environment-specific settings
# Wildcard value set because this application running in container
# https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/#environment-specific-settings
ALLOWED_HOSTS = config.ALLOWED_HOSTS

# Application definition
INSTALLED_APPS = config.INSTALLED_APPS

# Middleware
# https://docs.djangoproject.com/en/2.2/topics/http/middleware/
MIDDLEWARE = config.MIDDLEWARE

# Urls
# https://docs.djangoproject.com/en/2.2/ref/settings/
ROOT_URLCONF = config.ROOT_URLCONF

# Templates
# https://docs.djangoproject.com/en/2.2/topics/templates/
TEMPLATES = config.TEMPLATES

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = config.AUTH_PASSWORD_VALIDATORS

# Substituting a custom User model
# https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = config.AUTH_USER_MODEL

# Specifying authentication backends
# https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#specifying-authentication-backends
AUTHENTICATION_BACKENDS = config.AUTHENTICATION_BACKENDS

# Ldap configuration to single sign-on
# Application definitions
LDAP_RESOURCE = config.LDAP_RESOURCE
LDAP_HOST = config.LDAP_HOST
LDAP_USER = config.LDAP_USER
LDAP_PASS = config.LDAP_PASS

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = config.LANGUAGE_CODE
TIME_ZONE = config.TIME_ZONE
USE_I18N = config.USE_I18N
USE_L10N = config.USE_L10N
USE_TZ = config.USE_TZ

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'www', 'media')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "www")]

# Messages Tags
# https://docs.djangoproject.com/en/2.2/ref/contrib/messages/#message-tags
MESSAGE_TAGS = config.MESSAGE_TAGS

# Locale path
# https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-LOCALE_PATHS
LOCALE_PATHS = config.LOCALE_PATHS

# Filebrowser Extensions
# https://django-filebrowser.readthedocs.io/en/latest/settings.html#extensions
FILEBROWSER_EXTENSIONS = config.FILEBROWSER_EXTENSIONS
FILEBROWSER_DIRECTORY = config.FILEBROWSER_DIRECTORY

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'roomReservation',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Email
# https://docs.djangoproject.com/en/2.2/topics/email/
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_USER = 'acd6541f69479b'
EMAIL_HOST_PASSWORD = '787c30c6f9d530'
EMAIL_PORT = '2525'
