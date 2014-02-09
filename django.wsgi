#! -*- coding: utf-8 -*-

import os, sys
sys.path.append('/var/django/')
sys.path.append('/var/django/gaviota/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'gaviota.settings-produccion'

import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
    return _application(environ, start_response)