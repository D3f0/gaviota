#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.views.generic import list_detail
from gaviota.apps.aulas.views import index
from gaviota.apps.aulas.views import horario_aula, mostrar_edificio
from gaviota.apps.aulas.views import estadisticas_utilizacion
from datetime import datetime as dt
from datetime import timedelta as td

from gaviota.apps.aulas.admin import site
from apps.aulas import views #import horario_aula_excel, superposiciones,\
    #horario_carrera, horario_carrera_excel, sin_asignar, horario_dia
 
#urlpatterns = patterns('django.views.generic.simple',
#    ('^$', 'direct_to_template', {'template':'aulas/index.html'}),
#) 

dt2m_d_y = lambda dt: {'m': dt.month, 'd': dt.day, 'y': dt.year, }

urlpatterns = patterns('',
    (r'^$', index, ),
    (r'^buscar-simple/$', views.busqueda_simple, ),
    
    (r'^horario_aula/(?P<id>\d{1,5})/$', horario_aula),
    (r'^horario_aula/(?P<id>\d{1,5})/excel/$', views.horario_aula_excel_xlwt),
    
    (r'^edificio/(?P<edificio_id>\d{1,3})/$', mostrar_edificio),
    
    
    (r'^estadisticas/utilizacion/$', views.estadisticas_utilizacion),
    
    (r'^superposiciones/$', views.superposiciones),
    
    (r'^sin_asignar/$', views.sin_asignar),
    
    
    (r'^horario_carrera/(?P<carrera_id>\d{1,3})/$', views.horario_carrera),   
    (r'^horario_carrera/(?P<carrera_id>\d{1,3})/excel/$', views.horario_carrera_excel),
    
    (r'^horario_por_dia/(?P<n_dia>\d{1,3})/$', views.horario_dia),
    
    (r'^(?P<y>\d{4})/(?P<m>\d{1,2})/(?P<d>\d{1,2})/$', views.mostrar_dia,),
    
    
    (r'^tabla/', views.tabla, ),
    
    # TODO: Pedido
    #(r'^pedidos/$', views.pedidos, ),
    
    (r'^admin/(.*)', site.root)
)
#===============================================================================
# Edición de asignaturas
#===============================================================================
urlpatterns += patterns('django.views.generic.simple',
    (r'^asignatura/editar/$', 'direct_to_template', {'template': 'aulas/asignatura/editar.html'},),
)



#===============================================================================
# urlpatterns para listado cronológico. 
#===============================================================================
urlpatterns += patterns('django.views.generic.simple',
    (r'^listado/hoy/$', 'redirect_to', {'url': dt.now().strftime('../%Y/%m/%d/'), } ),
    (r'^listado/prevday/$', 'redirect_to', {'url': (dt.now() + td(days = -1)).strftime('../%Y/%m/%d/'), } ),
    (r'^listado/nextday/$', 'redirect_to', {'url': (dt.now() + td(days = -1)).strftime('../%Y/%m/%d/'), } ),
)

#===============================================================================
# urlpatterns para ayuda
#===============================================================================
urlpatterns += patterns('django.views.generic.simple',
    (r'^ayuda', 'direct_to_template', {'template':'aulas/ayuda.html'}),
)