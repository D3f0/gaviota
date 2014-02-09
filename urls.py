#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
    
# Adminsitración
from django.contrib import admin
admin.autodiscover()

# Root
urlpatterns = patterns('django.views.generic.simple',
    (r'^$', 'redirect_to', {'url': '/aulas/'}),
    
)

urlpatterns += patterns('',
    
    # Aplicacion de aulas
    (r'^aulas/', include('gaviota.apps.aulas.urls')),
    
    (r'^login/', 'gaviota.views.user_login'),
    (r'^logout/', 'gaviota.views.user_logout'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Admin de root
    (r'^admin/(.*)', admin.site.root),
)

# Snippet extraido de 
# http://oebfare.com/blog/2007/dec/31/django-and-static-files/
if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns("django.views",
        url(r"%s(?P<path>.*)$" % settings.MEDIA_URL[1:], "static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )
if settings.DEBUG_TOOLBAR:
    from debug_toolbar.urls import urlpatterns as debug_urlpatterns
    urlpatterns += debug_urlpatterns
