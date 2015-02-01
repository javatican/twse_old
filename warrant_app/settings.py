"""
Django settings for warrant_app project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_PATH = os.path.abspath(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nbl85!69q81dsl)3tp7vjv0i%bmww*qii4g(*ca)l&os&01d@^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'django_crontab',
    'django_extensions',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'warrant_app.urls'

WSGI_APPLICATION = 'warrant_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'warrant_db',  # Or path to database file if using sqlite3.
        'USER': 'pythonieh',  # Not used with sqlite3.
        'PASSWORD': 'M27328703',  # Not used with sqlite3.
        'HOST': 'db',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',  # Set to empty string for default. Not used with sqlite3.
        'TEST_CHARSET' : 'utf8',
        'TEST_COLLATION' : 'utf8_general_ci',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-tw'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = os.path.join(_PATH, 'static') 
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(_PATH, 'upload') 
MEDIA_URL = '/media/'

LOCALE_PATHS = (
    os.path.join(_PATH, 'locale'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'db_logging':{
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'warrant_app_db_statement.log'),
            'formatter': 'verbose',
        },
        'warrant_app':{
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'warrant_app_debug.log'),
            'formatter': 'verbose',
        },
        'cronjob':{
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'warrant_app_cronjob.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['db_logging'],
        },
        'warrant_app': {
            'handlers': ['console', 'warrant_app'],
            'level': 'DEBUG',
        },
        'warrant_app.cronjob': {
            'handlers': ['console', 'cronjob'],
            'level': 'DEBUG',
        },
    }
}

TWSE_TRADING_DOWNLOAD_URL='http://www.twse.com.tw/ch/trading/fund/T86/T86.php'
TWSE_PRICE_DOWNLOAD_URL='http://www.twse.com.tw/ch/trading/exchange/MI_INDEX/MI_INDEX.php'
TWSE_DOWNLOAD_URL_1='http://www.twse.com.tw/en/trading/fund/TWT43U/TWT43U.php'
TWSE_DOWNLOAD_A=os.path.join(BASE_DIR, 'twse_download_a')
TWSE_DOWNLOAD_B=os.path.join(BASE_DIR, 'twse_download_b')
TWSE_DOWNLOAD_C=os.path.join(BASE_DIR, 'twse_download_c')
TWSE_DOWNLOAD_D=os.path.join(BASE_DIR, 'twse_download_d')
TWSE_DOWNLOAD_0=os.path.join(BASE_DIR, 'twse_download0')
TWSE_DOWNLOAD_1=os.path.join(BASE_DIR, 'twse_download1')
TWSE_DOWNLOAD_2=os.path.join(BASE_DIR, 'twse_download2')
TWSE_DOWNLOAD_3=os.path.join(BASE_DIR, 'twse_download3')
TWSE_DOWNLOAD_4=os.path.join(BASE_DIR, 'twse_download4')
TWSE_DOWNLOAD_5=os.path.join(BASE_DIR, 'twse_download5')