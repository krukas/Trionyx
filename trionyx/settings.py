"""
trionyx.settings
~~~~~~~~~~~~~~~~

All Trionyx base settings

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""

INSTALLED_APPS = [
    # Trionyx apps
    'trionyx.core',

    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==============================================================================
# Project URLS and media settings
# ==============================================================================
ROOT_URLCONF = 'trionyx.urls'

LOGIN_URL = 'trionyx:login'
LOGOUT_URL = 'trionyx:logout'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

WSGI_APPLICATION = 'wsgi.application'


# ==============================================================================
# Middleware
# ==============================================================================
MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',

    #'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',

	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',

	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'trionyx.core.middleware.LoginRequiredMiddleware',
)


# ==============================================================================
# Auth / security
# ==============================================================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGIN_EXEMPT_URLS = [
	'static',
]

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


# ==============================================================================
# Templates
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

STATIC_URL = '/static/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'


# ==============================================================================
# Compressor
# ==============================================================================
STATICFILES_FINDERS = [
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = True


# ==============================================================================
# Cache backend
# ==============================================================================
CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
		'LOCATION': 'django_cache',
	}
}

CORS_ORIGIN_WHITELIST = [
    'localhost:8000',
    'localhost:4200',
]
