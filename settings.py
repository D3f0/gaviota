#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Settings de desarrollo
import sys
import os



DEBUG = True
TEMPLATE_DEBUG = DEBUG
# Switch para serivcio de medios estáticos
LOCAL_DEVELOPMENT = True

# Bandera de depuracion
DEBUG_TOOLBAR = False
DATABASE = 'sqlite'

if LOCAL_DEVELOPMENT:
    sys.path.append('..') # Asumimos Descom en el nivel superior

# Si da error, fuiste
#import descom

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

if DATABASE is 'mysql':
    DATABASE_ENGINE = 'mysql'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = 'gaviota'             # Or path to database file if using sqlite3.
    DATABASE_USER = 'gaviota'             # Not used with sqlite3.
    DATABASE_PASSWORD = '1234'         # Not used with sqlite3.
    DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

elif DATABASE is 'sqlite':
    DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = 'db/sqlite.dev.db'             # Or path to database file if using sqlite3.
    DATABASE_USER = ''             # Not used with sqlite3.
    DATABASE_PASSWORD = ''         # Not used with sqlite3.
    DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Argentina/BuenosAires'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-ar'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g)r)gz&bp-^nfx)bb$^!@#z&^6oinm06rl%9zklu2hsxfg&0c+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',

    # Middlewares de Descom
    #'descom.middleware.yui.YUIIncludeMiddleware',
    #'descom.middleware.threadlocals.ThreadLocals',
)

ROOT_URLCONF = 'gaviota.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (

    # Aplicaicones de provistas por django
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    # Aplicaciones de usuario
    'gaviota.apps.aulas',

    # Aplicaciones de soporte
    #'descom.contrib.extra_tags',

)


#===============================================================================
# Si el sitema no está corriendo en /, introducir el path a la aplicacion
# en esta variable.
#===============================================================================
BASE_URL = ''

try:
    import django_extensions
except ImportError:
    pass
else:
    INSTALLED_APPS += ('django_extensions', )



TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    # Gaviota
    'gaviota.apps.aulas.context_processors.edificios',
    # Descom
    'gaviota.context_processors.settings.MEDIA_URL',
    'gaviota.context_processors.settings.TEMPLATE_DEBUG',
    'gaviota.context_processors.settings.DIAS_SEMANA',
    'gaviota.context_processors.settings.HORAS',
)

#===============================================================================
# DESCOM YUI Inclusion
#===============================================================================
YUI_VERSION = '2.5.2'
YUI_INCLUDE_BASE = '/static/js/build/'
#------------------------------------------------------------------------------

#===============================================================================
# Configuración de la aplicación
#===============================================================================
CHARFIELD_MAX_LEN = 250

#===============================================================================
# Datetime
#===============================================================================

DATETIME_FORMAT = '%D/%M/%Y'


#===============================================================================
# logging
#===============================================================================
import logging
LOG_FILE = 'gaviota.log'
LOG_LEVEL = logging.DEBUG

# ----------------------------------------------------------
# Debug toolbar django
# ----------------------------------------------------------

try:
    import debug_toolbar
except ImportError:
    pass
else:
    INTERNAL_IPS = ('127.0.0.1',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

    INSTALLED_APPS += ('debug_toolbar', )


try:
    from gaviota.local_settings import *
except ImportError:
    pass

